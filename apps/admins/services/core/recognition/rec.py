import cv2
import numpy as np
import torch
import os
import torch.nn.functional as F
from torchvision import transforms
import ast
from apps.admins.services.core.recognition.ghostfacenetsv2 import GhostFaceNetsV2

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # thư mục detection
CORE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # sang thư mục core
WEIGHT_PATH = os.path.join(CORE_DIR, "weights", "0.9988571428571429.pt")
class FaceRecognition:
    """
    Face recognition using GhostFaceNetsV2 model.

    Args:
        weight_path (str): Path to model weights
        device (str): Device to run model on ('cuda' or 'cpu')
        batch_size (int): Batch size for processing
        threshold (float): Recognition threshold (default: 0.85)
        image_size (int): Input image size (default: 112)
        width (float): Model width multiplier (default: 1.3)
        dropout (float): Dropout rate (default: 0.2)
        use_flip (bool): Use horizontal flip augmentation (default: True)
    """

    def __init__(
            self,
            weight_path="core/weights/0.9988571428571429.pt",
            device=None,
            batch_size=32,
            threshold=0.85,
            image_size=112,
            width=1.3,
            dropout=0.2,
            use_flip=True
    ):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        self.threshold = threshold
        self.image_size = image_size
        self.use_flip = use_flip

        # Initialize model
        self.model = self._load_model(weight_path, image_size, width, dropout)

        # Initialize transforms
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((image_size, image_size)),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

        # Database of known faces
        self.database = []  # List of dicts with 'id', 'name', 'vector'
        self.database_vectors = None  # Tensor of all vectors

    def _load_model(self, weight_path, image_size, width, dropout):
        """Load GhostFaceNetsV2 model."""
        model = GhostFaceNetsV2(
            image_size=image_size,
            width=width,
            dropout=dropout,
            fp16=False
        )

        state_dict = torch.load(weight_path, map_location=self.device)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()

        print(f"Model loaded successfully from {weight_path}")
        return model

    @staticmethod
    def l2_normalize(tensor, dim=1):
        """
        L2 normalization of tensor.

        Args:
            tensor (torch.Tensor): Input tensor
            dim (int): Dimension to normalize

        Returns:
            torch.Tensor: Normalized tensor
        """
        norm = torch.norm(tensor, 2, dim, True)
        output = torch.div(tensor, norm)
        return output

    def _preprocess_face(self, face_img):
        """
        Preprocess a single face image.

        Args:
            face_img (np.ndarray): Face image (BGR format)

        Returns:
            torch.Tensor: Preprocessed tensor
        """
        # Convert BGR to RGB if needed
        if len(face_img.shape) == 3 and face_img.shape[2] == 3:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        return self.transform(face_img)

    def extract_features(self, faces, use_flip=None):
        """
        Extract feature vectors from face images.

        Args:
            faces (list): List of face images (np.ndarray)
            use_flip (bool): Use flip augmentation (default: use class setting)

        Returns:
            torch.Tensor: Feature vectors [N, D]
        """
        if use_flip is None:
            use_flip = self.use_flip

        if not faces:
            return torch.empty(0, 512).to(self.device)  # Empty tensor

        # Preprocess faces
        face_tensors = []
        flipped_tensors = []

        for face in faces:
            face_tensor = self._preprocess_face(face)
            face_tensors.append(face_tensor)

            if use_flip:
                flipped_face = cv2.flip(face, 1)  # Horizontal flip
                flipped_tensor = self._preprocess_face(flipped_face)
                flipped_tensors.append(flipped_tensor)

        # Stack and move to device
        face_batch = torch.stack(face_tensors).to(self.device)

        # Extract features
        with torch.no_grad():
            features = self.model(face_batch)

            if use_flip:
                flipped_batch = torch.stack(flipped_tensors).to(self.device)
                flipped_features = self.model(flipped_batch)
                features = features + flipped_features

        # L2 normalize
        features = self.l2_normalize(features)

        return features

    def add_to_database(self, face_id, name, face_img=None, vector=None):
        """
        Add a face to the recognition database.

        Args:
            face_id (str): Unique identifier (e.g., student ID)
            name (str): Name of the person
            face_img (np.ndarray): Face image (if vector not provided)
            vector (torch.Tensor or list): Pre-computed feature vector

        Returns:
            bool: Success status
        """
        if vector is None and face_img is None:
            raise ValueError("Either face_img or vector must be provided")

        # Extract vector if not provided
        if vector is None:
            features = self.extract_features([face_img])
            vector = features[0].cpu()
        else:
            # Convert to tensor if needed
            if isinstance(vector, (list, str)):
                if isinstance(vector, str):
                    vector = ast.literal_eval(vector)
                vector = torch.tensor(vector, dtype=torch.float32)

            if not isinstance(vector, torch.Tensor):
                vector = torch.tensor(vector, dtype=torch.float32)

        # Add to database
        self.database.append({
            'id': face_id,
            'name': name,
            'vector': vector
        })

        # Rebuild database vectors
        self._rebuild_database_vectors()

        return True

    def load_database(self, database_list):
        """
        Load multiple entries into database.

        Args:
            database_list (list): List of dicts with 'id', 'name', 'vector'
                Example: [{'MSSV': '123', 'name': 'John', 'vector': '[0.1, 0.2, ...]'}, ...]
        """
        self.database = []

        for entry in database_list:
            face_id = entry.get('MSSV') or entry.get('id')
            name = entry.get('name')
            vector = entry.get('vector')

            if vector is not None:
                self.add_to_database(face_id, name, vector=vector)

        print(f"Loaded {len(self.database)} entries into database")

    def _rebuild_database_vectors(self):
        """Rebuild the database vectors tensor."""
        if not self.database:
            self.database_vectors = None
            return

        vectors = [entry['vector'] for entry in self.database]
        self.database_vectors = torch.stack(vectors).to(self.device)
        print(f"Database vectors shape: {self.database_vectors.shape}")

    def compare_vectors(self, query_vectors, database_vectors=None, threshold=None):
        """
        Compare query vectors with database vectors using Euclidean distance.

        Args:
            query_vectors (torch.Tensor): Query vectors [N, D]
            database_vectors (torch.Tensor): Database vectors [M, D]
            threshold (float): Distance threshold for matching

        Returns:
            torch.Tensor: Binary tensor [N, M], each row has at most one 1
        """
        if database_vectors is None:
            database_vectors = self.database_vectors

        if threshold is None:
            threshold = self.threshold

        if database_vectors is None or len(database_vectors) == 0:
            return torch.zeros(len(query_vectors), 1, dtype=torch.int)

        # Ensure float type
        query_vectors = query_vectors.float()
        database_vectors = database_vectors.float()

        # Compute Euclidean distance [N, M]
        distances = torch.cdist(query_vectors, database_vectors, p=2)

        # Find minimum distance and corresponding index for each query
        min_dist, min_idx = torch.min(distances, dim=1)

        # Initialize result with zeros
        result = torch.zeros_like(distances, dtype=torch.int)

        # Set 1 only if minimum distance is below threshold
        for i in range(distances.size(0)):
            if min_dist[i] < threshold:
                result[i, min_idx[i]] = 1

        return result

    def recognize_faces(self, face_dicts, return_vectors=False):
        """
        Recognize faces from a list of face dictionaries.

        Args:
            face_dicts (list): List of dicts with 'img' key (face image)
            return_vectors (bool): Return feature vectors

        Returns:
            list: Updated face_dicts with 'id', 'name', and optionally 'vector'
        """
        if not self.database:
            print("Warning: Database is empty. All faces will be marked as Unknown.")

        # Process in batches
        batch_faces = []
        batch_indices = []
        all_vectors = []

        for idx, face_dict in enumerate(face_dicts):
            face_img = face_dict.get('img')
            if face_img is None:
                continue

            batch_faces.append(face_img)
            batch_indices.append(idx)

            # Process batch when full or at the end
            if len(batch_faces) >= self.batch_size or idx == len(face_dicts) - 1:
                # Extract features
                features = self.extract_features(batch_faces)

                if return_vectors:
                    all_vectors.extend([v.cpu() for v in features])

                # Compare with database
                if self.database_vectors is not None:
                    matches = self.compare_vectors(features, self.database_vectors, self.threshold)

                    # Update face_dicts with recognition results
                    for i, result in enumerate(matches):
                        face_idx = batch_indices[i]

                        if result.sum() > 0:  # Match found
                            db_idx = torch.where(result == 1)[0].item()
                            face_dicts[face_idx]['id'] = self.database[db_idx]['id']
                            face_dicts[face_idx]['name'] = self.database[db_idx]['name']
                        else:  # No match
                            face_dicts[face_idx]['id'] = "Unknown"
                            face_dicts[face_idx]['name'] = "Unknown"

                        if return_vectors:
                            face_dicts[face_idx]['vector'] = all_vectors[i]
                else:
                    # No database, mark all as unknown
                    for i in range(len(batch_faces)):
                        face_idx = batch_indices[i]
                        face_dicts[face_idx]['id'] = "Unknown"
                        face_dicts[face_idx]['name'] = "Unknown"

                        if return_vectors:
                            face_dicts[face_idx]['vector'] = all_vectors[i]

                # Reset batch
                batch_faces = []
                batch_indices = []

        return face_dicts

    def recognize_single(self, face_img):
        """
        Recognize a single face image.

        Args:
            face_img (np.ndarray): Face image

        Returns:
            dict: Recognition result with 'id', 'name', 'distance', 'vector'
        """
        # Extract features
        features = self.extract_features([face_img])

        if self.database_vectors is None or len(self.database_vectors) == 0:
            return {
                'id': 'Unknown',
                'name': 'Unknown',
                'distance': float('inf'),
                'vector': features[0].cpu()
            }

        # Compute distances
        distances = torch.cdist(features, self.database_vectors, p=2)
        min_dist, min_idx = torch.min(distances, dim=1)

        min_dist = min_dist.item()
        min_idx = min_idx.item()

        # Check threshold
        if min_dist < self.threshold:
            return {
                'id': self.database[min_idx]['id'],
                'name': self.database[min_idx]['name'],
                'distance': min_dist,
                'vector': features[0].cpu()
            }
        else:
            return {
                'id': 'Unknown',
                'name': 'Unknown',
                'distance': min_dist,
                'vector': features[0].cpu()
            }

    def clear_database(self):
        """Clear the recognition database."""
        self.database = []
        self.database_vectors = None
        print("Database cleared")

    def get_database_info(self):
        """Get information about the current database."""
        return {
            'num_entries': len(self.database),
            'ids': [entry['id'] for entry in self.database],
            'names': [entry['name'] for entry in self.database]
        }


# Usage example
if __name__ == "__main__":
    # Initialize recognition system
    recognizer = FaceRecognition(
        weight_path=WEIGHT_PATH,
        device="cuda" if torch.cuda.is_available() else "cpu",
        batch_size=32,
        threshold=0.85
    )
    # Load database from list of students
    # Or add individual faces

    face_img = cv2.imread(f"{CORE_DIR}/image/N21DCCN054.jpg")
    results = recognizer.extract_features([face_img])
    print(results)
