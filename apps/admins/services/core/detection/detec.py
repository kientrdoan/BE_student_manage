import os
import cv2
import numpy as np
import torch
from skimage import transform as trans
from  apps.admins.services.core.detection.prior_box import PriorBox
from  apps.admins.services.core.detection.retinaface import RetinaFace
from apps.admins.services.core.detection.box_utils import decode, decode_landm
from apps.admins.services.core.detection.custom_config import cfg_mnet
from apps.admins.services.core.detection.py_cpu_nms import py_cpu_nms

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # thư mục detection
CORE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # sang thư mục core
WEIGHT_PATH = os.path.join(CORE_DIR, "weights", "mobilenet0.25_Final.pth")
class FaceDetector:
    """
    Face detection and alignment using RetinaFace model.

    Args:
        img_width (int): Input image width (default: 1280)
        img_height (int): Input image height (default: 720)
        device (str): Device to run model on ('cuda' or 'cpu')
        weight_path (str): Path to model weights
        confidence_threshold (float): Minimum confidence score for detection
        nms_threshold (float): NMS threshold for removing duplicate detections
        vis_threshold (float): Visualization threshold for display
        cfg: Model configuration (default: cfg_mnet)
    """

    def __init__(
            self,
            img_width=1280,
            img_height=720,
            device='cuda',
            weight_path=WEIGHT_PATH,
            confidence_threshold=0.4,
            nms_threshold=0.2,
            vis_threshold=0.9,
            top_k=1000,
            keep_top_k=100,
            cfg=cfg_mnet
    ):
        self.device = device
        self.cfg = cfg
        self.weight_path = weight_path
        self.im_width = img_width
        self.im_height = img_height

        # Detection parameters
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.vis_threshold = vis_threshold
        self.top_k = top_k
        self.keep_top_k = keep_top_k
        self.resize = 1

        # Load model
        self.net = self._load_model()
        self.prior_data = self._create_prior_box()

        # Preprocessing parameters
        self.mean = np.array([104, 117, 123], dtype=np.float32)

        # Alignment template (standard face landmarks)
        self.dst_landmarks = np.array([
            [30.2946, 51.6963],
            [65.5318, 51.5014],
            [48.0252, 71.7366],
            [33.5493, 92.3655],
            [62.7299, 92.2041]
        ], dtype=np.float32)
        self.dst_landmarks[:, 0] += 8.0

    def _load_model(self):
        """Load RetinaFace model from weights."""
        print(f'Loading pretrained model from {self.weight_path}')

        net = RetinaFace(cfg=self.cfg, phase='test')
        pretrained_dict = torch.load(
            self.weight_path,
            map_location=lambda storage, loc: storage
        )

        # Remove 'module.' prefix if exists
        pretrained_dict = self._remove_prefix(pretrained_dict, 'module.')

        net.load_state_dict(pretrained_dict, strict=False)
        net.eval()
        net = net.to(self.device)

        print('Model loaded successfully!')
        return net

    def _create_prior_box(self):
        """Create prior boxes for detection."""
        priorbox = PriorBox(
            self.cfg,
            image_size=(self.im_height, self.im_width)
        )
        priors = priorbox.forward()
        priors = priors.to(self.device)
        return priors.data

    @staticmethod
    def _remove_prefix(state_dict, prefix):
        """Remove prefix from state dict keys."""
        f = lambda x: x.split(prefix, 1)[-1] if x.startswith(prefix) else x
        return {f(key): value for key, value in state_dict.items()}

    def _preprocess(self, img):
        """Preprocess image for model input."""
        img = img.astype(np.float32)
        img -= self.mean
        img = img.transpose(2, 0, 1)  # HWC -> CHW
        img = torch.from_numpy(img).unsqueeze(0)  # Add batch dimension
        return img.to(self.device)

    def align_face(self, img, landmarks):
        """
        Align face using similarity transformation.

        Args:
            img (np.ndarray): Input image
            landmarks (np.ndarray): Face landmarks (5 points)

        Returns:
            np.ndarray: Aligned face image (112x112)
        """
        src = landmarks.astype(np.float32)
        tform = trans.SimilarityTransform()
        tform.estimate(src, self.dst_landmarks)
        M = tform.params[0:2, :]
        aligned = cv2.warpAffine(img, M, (112, 112), borderValue=0.0)
        return aligned

    def detect_single(self, img, return_aligned=True, save_results=False, save_dir="aligned_faces"):
        """
        Detect faces in a single image.

        Args:
            img (np.ndarray): Input image (BGR format)
            return_aligned (bool): Return aligned faces
            save_results (bool): Save detection results to disk
            save_dir (str): Directory to save results

        Returns:
            tuple: (faces, boxes, scores, landmarks)
                - faces: List of aligned face images (if return_aligned=True)
                - boxes: List of bounding boxes [x1, y1, x2, y2]
                - scores: List of confidence scores
                - landmarks: List of facial landmarks
        """
        img_tensor = self._preprocess(img)

        # Forward pass
        with torch.no_grad():
            loc, conf, landms = self.net(img_tensor)

        # Decode predictions
        scale = torch.Tensor([self.im_width, self.im_height,
                              self.im_width, self.im_height]).to(self.device)

        boxes = decode(loc.data.squeeze(0), self.prior_data, self.cfg['variance'])
        boxes = boxes * scale / self.resize
        boxes = boxes.cpu().numpy()

        scores = conf.squeeze(0).data.cpu().numpy()[:, 1]

        scale_landm = torch.Tensor([
            self.im_width, self.im_height, self.im_width, self.im_height,
            self.im_width, self.im_height, self.im_width, self.im_height,
            self.im_width, self.im_height
        ]).to(self.device)

        landms_decoded = decode_landm(landms.data.squeeze(0),
                                      self.prior_data,
                                      self.cfg['variance'])
        landms_decoded = landms_decoded * scale_landm / self.resize
        landms_decoded = landms_decoded.cpu().numpy()

        # Filter by confidence
        inds = np.where(scores > self.confidence_threshold)[0]
        boxes = boxes[inds]
        landms_decoded = landms_decoded[inds]
        scores = scores[inds]

        # Keep top-K before NMS
        order = scores.argsort()[::-1][:self.top_k]
        boxes = boxes[order]
        landms_decoded = landms_decoded[order]
        scores = scores[order]

        # Apply NMS
        dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32)
        keep = py_cpu_nms(dets, self.nms_threshold)
        dets = dets[keep, :]
        landms_decoded = landms_decoded[keep]

        # Keep top-K after NMS
        dets = dets[:self.keep_top_k, :]
        landms_decoded = landms_decoded[:self.keep_top_k, :]

        # Process results
        faces = []
        valid_boxes = []
        valid_scores = []
        valid_landmarks = []

        if save_results:
            os.makedirs(save_dir, exist_ok=True)

        for i, (det, landm) in enumerate(zip(dets, landms_decoded)):
            score = det[4]
            if score < self.vis_threshold:
                continue

            box = det[:4].astype(int)
            landmarks = landm.reshape(5, 2)

            valid_boxes.append(box)
            valid_scores.append(score)
            valid_landmarks.append(landmarks)

            if return_aligned:
                aligned_face = self.align_face(img, landmarks)
                faces.append(aligned_face)

                if save_results:
                    # Save raw crop
                    x1, y1, x2, y2 = box
                    cropped_raw = img[y1:y2, x1:x2]
                    cv2.imwrite(os.path.join(save_dir, f"face_{i}_raw.jpg"), cropped_raw)
                    cv2.imwrite(os.path.join(save_dir, f"face_{i}_aligned.jpg"), aligned_face)

        return faces, valid_boxes, valid_scores, valid_landmarks

    def detect_batch(self, batch_imgs):
        """
        Detect faces in a batch of images.

        Args:
            batch_imgs (list): List of input images (BGR format)

        Returns:
            list: List of dictionaries, each containing:
                - 'img': aligned face image
                - 'box': bounding box
                - 'score': confidence score
                - 'landmarks': facial landmarks
                - 'image_idx': index of source image in batch
        """
        # Preprocess batch
        batch_tensors = []
        for img in batch_imgs:
            img_tensor = self._preprocess(img)
            batch_tensors.append(img_tensor)

        batch = torch.cat(batch_tensors, dim=0)

        # Forward pass
        with torch.no_grad():
            all_loc, all_conf, all_landms = self.net(batch)

        # Process each image in batch
        batch_results = []

        for img_idx, (loc, conf, landm, img) in enumerate(
                zip(all_loc, all_conf, all_landms, batch_imgs)
        ):
            # Decode predictions
            scale = torch.Tensor([self.im_width, self.im_height,
                                  self.im_width, self.im_height]).to(self.device)

            boxes = decode(loc.squeeze(0), self.prior_data, self.cfg['variance'])
            boxes = boxes * scale / self.resize
            boxes = boxes.detach().cpu().numpy()

            scores = conf.squeeze(0).data.detach().cpu().numpy()[:, 1]

            scale_landm = torch.Tensor([
                self.im_width, self.im_height, self.im_width, self.im_height,
                self.im_width, self.im_height, self.im_width, self.im_height,
                self.im_width, self.im_height
            ]).to(self.device)

            landms_decoded = decode_landm(landm.squeeze(0),
                                          self.prior_data,
                                          self.cfg['variance'])
            landms_decoded = landms_decoded * scale_landm / self.resize
            landms_decoded = landms_decoded.detach().cpu().numpy()

            # Filter and NMS
            inds = np.where(scores > self.confidence_threshold)[0]
            boxes = boxes[inds]
            landms_decoded = landms_decoded[inds]
            scores = scores[inds]

            order = scores.argsort()[::-1][:self.top_k]
            boxes = boxes[order]
            landms_decoded = landms_decoded[order]
            scores = scores[order]

            dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32)
            keep = py_cpu_nms(dets, self.nms_threshold)
            dets = dets[keep, :]
            landms_decoded = landms_decoded[keep]

            dets = dets[:self.keep_top_k, :]
            landms_decoded = landms_decoded[:self.keep_top_k, :]

            # Create face dictionaries
            for det, landm in zip(dets, landms_decoded):
                if det[4] < self.vis_threshold:
                    continue

                face_dict = {
                    'box': det[:4].astype(int),
                    'score': det[4],
                    'landmarks': landm.reshape(5, 2),
                    'img': self.align_face(img, landm.reshape(5, 2)),
                    'image_idx': img_idx
                }
                batch_results.append(face_dict)

        return batch_results

    def visualize(self, img, boxes, scores, landmarks, save_path=None):
        """
        Visualize detection results on image.

        Args:
            img (np.ndarray): Input image
            boxes (list): List of bounding boxes
            scores (list): List of confidence scores
            landmarks (list): List of facial landmarks
            save_path (str): Path to save visualization (optional)

        Returns:
            np.ndarray: Image with visualizations
        """
        img_vis = img.copy()

        for box, score, landm in zip(boxes, scores, landmarks):
            # Draw bounding box
            x1, y1, x2, y2 = box
            cv2.rectangle(img_vis, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # Draw confidence score
            text = f"{score:.4f}"
            cv2.putText(img_vis, text, (x1, y1 + 12),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            # Draw landmarks
            colors = [(0, 0, 255), (0, 255, 255), (255, 0, 255),
                      (0, 255, 0), (255, 0, 0)]
            for i, (x, y) in enumerate(landm):
                cv2.circle(img_vis, (int(x), int(y)), 1, colors[i], 4)

        if save_path:
            cv2.imwrite(save_path, img_vis)

        return img_vis


# Usage example
if __name__ == "__main__":
    # Initialize detector


    # Single image detection
    print(f"{CORE_DIR}/football_team.jpg")
    img = cv2.imread(f"{CORE_DIR}/detection/football_team.jpg")
    detector = FaceDetector(
        img_width=img.shape[1],
        img_height=img.shape[0],
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    faces, boxes, scores, landmarks = detector.detect_single(img)

    # Visualize results
    img_vis = detector.visualize(img, boxes, scores, landmarks, save_path=f"{CORE_DIR}/detection/football_team_result.jpg")

    # Batch detection
    # batch_imgs = [cv2.imread(f"image_{i}.jpg") for i in range(5)]
    # batch_results = detector.detect_batch(batch_imgs)
    #
    # print(f"Detected {len(batch_results)} faces in batch")