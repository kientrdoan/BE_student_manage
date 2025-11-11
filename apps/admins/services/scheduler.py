import random
import copy
from typing import List, Tuple, Dict
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)


class Chromosome:
    """
    Nhiễm sắc thể - Biểu diễn một cách xếp lịch
    Mỗi gen = (teacher_id, room_id, day_idx, slot)
    """

    def __init__(self, courses, genes=None, hard_assignments=None):
        self.courses = courses  # Danh sách lớp tín chỉ
        self.genes = genes if genes else []  # Danh sách gen
        self.fitness = 0  # Điểm đánh giá
        self.hard_assignments = hard_assignments or []  # ← SỬA: Thêm or []

        if not genes:
            self.initialize_random()

    def initialize_random(self):
        """Khởi tạo gen ngẫu nhiên, tuân theo phân công cứng"""
        days = list(range(6))  # 0=Thứ2, 1=Thứ3,..., 5=Thứ7
        slots = [1, 2, 3, 4, 5, 6]  # ← SỬA: Thêm đầy đủ các tiết

        # Tạo map phân công cứng theo course_id
        hard_map = {ha.course_id: ha for ha in self.hard_assignments}

        for course in self.courses:
            # Lấy GV có thể dạy môn này
            eligible_teachers = self.get_eligible_teachers(course)
            # Lấy phòng phù hợp
            suitable_rooms = self.get_suitable_rooms(course)

            if eligible_teachers and suitable_rooms:
                # Kiểm tra có phân công cứng không
                hard_assign = hard_map.get(course.id)

                if hard_assign:
                    gene = {
                        'course_id': course.id,
                        'teacher_id': hard_assign.teacher_id,  # Cố định
                        'room_id': random.choice(suitable_rooms).id,  # Random
                        'day_idx': random.choice(days),
                        'slot': random.choice(slots),
                        'is_hard': True
                    }
                    logger.debug(f" - GV {hard_assign.teacher_id} - ")
                else:
                    # KHÔNG CÓ PHÂN CÔNG CỨNG - tạo ngẫu nhiên
                    gene = {
                        'course_id': course.id,
                        'teacher_id': random.choice(eligible_teachers).id,
                        'room_id': random.choice(suitable_rooms).id,
                        'day_idx': random.choice(days),
                        'slot': random.choice(slots),
                        'is_hard': False
                    }

                self.genes.append(gene)

    def get_eligible_teachers(self, course):
        """Lấy GV có thể dạy môn này"""
        from apps.my_built_in.models.giao_vien import GiaoVien

        subject = course.subject
        if not subject or not subject.major:
            return list(GiaoVien.objects.filter(is_deleted=False))

        # GV cùng khoa với môn học
        return list(GiaoVien.objects.filter(
            department=subject.major.department,
            is_deleted=False
        ))

    def get_suitable_rooms(self, course):
        """Lấy phòng phù hợp"""
        from apps.my_built_in.models.phong_hoc import PhongHoc

        capacity_needed = course.max_capacity
        return list(PhongHoc.objects.filter(
            is_active=True,
            max_capacity__gte=capacity_needed
        ))

    def __repr__(self):
        return f"Chromosome(fitness={self.fitness:.2f}, genes_count={len(self.genes)})"


class GeneticScheduler:
    """
    Thuật toán Genetic Algorithm cho xếp lịch học
    """

    # Tham số GA
    POPULATION_SIZE = 100  # Kích thước quần thể
    GENERATIONS = 200  # Số thế hệ tối đa
    CROSSOVER_RATE = 0.8  # Tỷ lệ lai ghép
    MUTATION_RATE = 0.05  # Tỷ lệ đột biến
    ELITISM_COUNT = 10  # Số cá thể ưu tú giữ lại
    TOURNAMENT_SIZE = 5  # Kích thước tournament

    # Trọng số fitness
    WEIGHT_SCHEDULED = 1000  # Điểm cơ bản cho mỗi lớp xếp được
    PENALTY_ROOM_CONFLICT = -1000  # Phạt trùng phòng
    PENALTY_TEACHER_CONFLICT = -1000  # Phạt trùng GV
    PENALTY_CLASS_CONFLICT = -1000  # Phạt trùng lớp SV
    PENALTY_ROOM_CAPACITY = -500  # Phạt phòng không đủ chỗ
    PENALTY_VIOLATE_HARD = -10000
    BONUS_MORNING = 10  # Thưởng tiết sáng
    BONUS_COMPACT = 5  # Thưởng lịch gọn

    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    def __init__(self, semester_id: int):
        self.semester_id = semester_id
        self.population = []
        self.best_chromosome = None
        self.best_fitness_history = []
        self.avg_fitness_history = []

    def get_courses_to_schedule(self):
        """Lấy danh sách lớp cần xếp"""
        from apps.my_built_in.models.lop_tin_chi import LopTinChi

        courses = LopTinChi.objects.filter(
            semester_id=self.semester_id,
            is_deleted=False,
            teacher_id__isnull=True
        ).select_related(
            'subject', 'class_st', 'subject__major', 'subject__major__department'
        ).annotate(
            enrolled_count=Count('dang_ky', filter=Q(dang_ky__is_deleted=False))
        )

        return list(courses)

    def get_hard_assignments(self,hard_assignments=None):
        """Lấy danh sách phân công cứng"""
        return hard_assignments if hard_assignments is not None else []

    def initialize_population(self, courses, hard_assignments=None):
        """Khởi tạo quần thể với hard_assignments"""
        logger.info(f"Đang khởi tạo quần thể {self.POPULATION_SIZE} cá thể...")

        if hard_assignments is None:
            hard_assignments = []

        self.population = []
        for i in range(self.POPULATION_SIZE):
            # ← SỬA: TRUYỀN hard_assignments vào Chromosome
            chromosome = Chromosome(courses, hard_assignments=hard_assignments)
            self.population.append(chromosome)

            if (i + 1) % 20 == 0:
                logger.info(f"  Đã tạo {i + 1}/{self.POPULATION_SIZE} cá thể")

    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """
        Tính điểm fitness cho một nhiễm sắc thể
        """
        fitness = 0
        violations = {
            'room_conflicts': 0,
            'teacher_conflicts': 0,
            'class_conflicts': 0,
            'capacity_issues': 0,
            'hard_violations': 0
        }

        # Điểm cơ bản: Số lớp xếp được
        fitness += len(chromosome.genes) * self.WEIGHT_SCHEDULED

        # Tạo map phân công cứng
        hard_map = {ha.course_id: ha for ha in chromosome.hard_assignments}

        # Kiểm tra ràng buộc
        schedule_map = {}  # (room_id, day, slot): course_id
        teacher_map = {}  # (teacher_id, day, slot): course_id
        class_map = {}  # (class_id, day, slot): course_id

        for gene in chromosome.genes:
            course = next((c for c in chromosome.courses if c.id == gene['course_id']), None)
            if not course:
                continue

            room_id = gene['room_id']
            teacher_id = gene['teacher_id']
            day = gene['day_idx']
            slot = gene['slot']
            course_id = gene['course_id']

            # ========== KIỂM TRA VI PHẠM PHÂN CÔNG CỨNG TRƯỚC ==========
            if course_id in hard_map:
                hard = hard_map[course_id]

                # Kiểm tra teacher
                if gene['teacher_id'] != hard.teacher_id:
                    fitness += self.PENALTY_VIOLATE_HARD
                    violations['hard_violations'] += 1
                    logger.debug(
                        f"Vi phạm GV: Course {course_id} - Expected {hard.teacher_id}, Got {gene['teacher_id']}")

            # ========== KIỂM TRA CÁC RÀNG BUỘC KHÁC ==========

            # 1. Kiểm tra trùng phòng
            room_key = (room_id, day, slot)
            if room_key in schedule_map:
                fitness += self.PENALTY_ROOM_CONFLICT
                violations['room_conflicts'] += 1
            else:
                schedule_map[room_key] = gene['course_id']

            # 2. Kiểm tra trùng giảng viên
            teacher_key = (teacher_id, day, slot)
            if teacher_key in teacher_map:
                fitness += self.PENALTY_TEACHER_CONFLICT
                violations['teacher_conflicts'] += 1
            else:
                teacher_map[teacher_key] = gene['course_id']

            # 3. Kiểm tra trùng lớp sinh viên
            if course.class_st:
                class_key = (course.class_st_id, day, slot)
                if class_key in class_map:
                    fitness += self.PENALTY_CLASS_CONFLICT
                    violations['class_conflicts'] += 1
                else:
                    class_map[class_key] = gene['course_id']

            # 4. Kiểm tra sức chứa phòng
            from apps.my_built_in.models.phong_hoc import PhongHoc
            try:
                room = PhongHoc.objects.get(id=room_id)
                if room.max_capacity < course.max_capacity:
                    fitness += self.PENALTY_ROOM_CAPACITY
                    violations['capacity_issues'] += 1
            except:
                pass

            # Ràng buộc mềm
            # 5. Thưởng tiết sáng (slot 1, 2)
            if slot in [1, 2]:
                fitness += self.BONUS_MORNING

        chromosome.fitness = fitness
        chromosome.violations = violations

        return fitness

    def evaluate_population(self):
        """Đánh giá fitness cho toàn bộ quần thể"""
        for chromosome in self.population:
            self.calculate_fitness(chromosome)

        # Sắp xếp theo fitness giảm dần
        self.population.sort(key=lambda x: x.fitness, reverse=True)

        # Lưu lại cá thể tốt nhất
        if not self.best_chromosome or self.population[0].fitness > self.best_chromosome.fitness:
            self.best_chromosome = copy.deepcopy(self.population[0])

        # Lưu lịch sử
        best_fit = self.population[0].fitness
        avg_fit = sum(c.fitness for c in self.population) / len(self.population)
        self.best_fitness_history.append(best_fit)
        self.avg_fitness_history.append(avg_fit)

    def tournament_selection(self) -> Chromosome:
        """
        Chọn lọc theo phương pháp Tournament
        """
        tournament = random.sample(self.population, self.TOURNAMENT_SIZE)
        tournament.sort(key=lambda x: x.fitness, reverse=True)
        return tournament[0]

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Lai ghép Single Point Crossover
        """
        if random.random() > self.CROSSOVER_RATE:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)

        # Chọn điểm cắt ngẫu nhiên
        point = random.randint(1, len(parent1.genes) - 1)

        # Tạo con
        child1_genes = parent1.genes[:point] + parent2.genes[point:]
        child2_genes = parent2.genes[:point] + parent1.genes[point:]

        # ← SỬA: Truyền hard_assignments
        child1 = Chromosome(parent1.courses, child1_genes, parent1.hard_assignments)
        child2 = Chromosome(parent2.courses, child2_genes, parent2.hard_assignments)

        return child1, child2

    def uniform_crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Lai ghép Uniform Crossover - GEN CỨNG ĐƯỢC GIỮ NGUYÊN
        """
        if random.random() > self.CROSSOVER_RATE:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)

        child1_genes = []
        child2_genes = []

        for g1, g2 in zip(parent1.genes, parent2.genes):
            # ← SỬA: Nếu là gen cứng, giữ nguyên cho cả 2 con
            if g1.get('is_hard', False):
                child1_genes.append(copy.deepcopy(g1))
                child2_genes.append(copy.deepcopy(g1))
            elif g2.get('is_hard', False):
                child1_genes.append(copy.deepcopy(g2))
                child2_genes.append(copy.deepcopy(g2))
            else:
                # Gen mềm: chọn ngẫu nhiên
                if random.random() < 0.5:
                    child1_genes.append(copy.deepcopy(g1))
                    child2_genes.append(copy.deepcopy(g2))
                else:
                    child1_genes.append(copy.deepcopy(g2))
                    child2_genes.append(copy.deepcopy(g1))

        # ← SỬA: Truyền hard_assignments
        child1 = Chromosome(parent1.courses, child1_genes, parent1.hard_assignments)
        child2 = Chromosome(parent2.courses, child2_genes, parent2.hard_assignments)

        return child1, child2

    def mutate(self, chromosome: Chromosome):
        """
        Đột biến - KHÔNG đột biến các gen đã phân công cứng
        """
        for i, gene in enumerate(chromosome.genes):
            # ← SỬA: BỎ QUA GEN CỨNG
            if gene.get('is_hard', False):
                continue

            if random.random() < self.MUTATION_RATE:
                # Lấy thông tin course
                course = next((c for c in chromosome.courses if c.id == gene['course_id']), None)
                if not course:
                    continue

                # Đột biến ngẫu nhiên một thuộc tính
                mutation_type = random.randint(0, 3)

                if mutation_type == 0:  # Đổi giảng viên
                    teachers = chromosome.get_eligible_teachers(course)
                    if teachers:
                        gene['teacher_id'] = random.choice(teachers).id

                elif mutation_type == 1:  # Đổi phòng
                    rooms = chromosome.get_suitable_rooms(course)
                    if rooms:
                        gene['room_id'] = random.choice(rooms).id

                elif mutation_type == 2:  # Đổi ngày
                    gene['day_idx'] = random.randint(0, 5)

                elif mutation_type == 3:  # Đổi tiết
                    gene['slot'] = random.choice([1, 2, 3, 4, 5, 6])

    def create_new_generation(self):
        """
        Tạo thế hệ mới
        """
        new_population = []

        # Elitism: Giữ lại các cá thể tốt nhất
        new_population.extend(copy.deepcopy(self.population[:self.ELITISM_COUNT]))

        # Tạo con mới bằng lai ghép
        while len(new_population) < self.POPULATION_SIZE:
            # Chọn 2 bố mẹ
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()

            # Lai ghép
            child1, child2 = self.uniform_crossover(parent1, parent2)

            # Đột biến
            self.mutate(child1)
            self.mutate(child2)

            # Thêm vào quần thể mới
            new_population.append(child1)
            if len(new_population) < self.POPULATION_SIZE:
                new_population.append(child2)

        self.population = new_population

    def run(self,hard_assignments) -> Dict:
        """
        Chạy thuật toán Genetic Algorithm
        """
        logger.info("=" * 60)
        logger.info("BẮT ĐẦU GENETIC ALGORITHM")
        logger.info("=" * 60)

        # Lấy danh sách lớp cần xếp
        courses = self.get_courses_to_schedule()
        logger.info(f"Số lớp cần xếp: {len(courses)}")

        if not courses:
            return {
                'success': True,
                'message': 'Không có lớp nào cần xếp lịch',
                'best_chromosome': None
            }

        # ← SỬA: Lấy phân công cứng

        logger.info(f"Số phân công cứng: {len(hard_assignments)}")

        if hard_assignments:
            for ha in hard_assignments:
                logger.info(f"  GV {ha.teacher_id}, ")
        else:
            logger.info("  Không có phân công cứng nào")

        # ← SỬA: Khởi tạo quần thể với hard_assignments
        self.initialize_population(courses, hard_assignments)

        # Đánh giá quần thể ban đầu
        self.evaluate_population()
        logger.info(f"Thế hệ 0: Best fitness = {self.population[0].fitness:.2f}")
        logger.info(f"         Violations = {self.population[0].violations}")

        # Tiến hóa qua các thế hệ
        no_improvement = 0
        best_fitness = self.population[0].fitness

        for generation in range(1, self.GENERATIONS + 1):
            # Tạo thế hệ mới
            self.create_new_generation()

            # Đánh giá
            self.evaluate_population()

            current_best = self.population[0].fitness
            current_avg = sum(c.fitness for c in self.population) / len(self.population)

            # Log progress
            if generation % 10 == 0:
                logger.info(
                    f"Thế hệ {generation}: "
                    f"Best = {current_best:.2f}, "
                    f"Avg = {current_avg:.2f}, "
                    f"Violations = {self.population[0].violations}"
                )

            # Kiểm tra cải thiện
            if current_best > best_fitness:
                best_fitness = current_best
                no_improvement = 0
            else:
                no_improvement += 1

            # Dừng sớm nếu không cải thiện
            if no_improvement >= 50:
                logger.info(f"Dừng sớm sau {generation} thế hệ (không cải thiện)")
                break

        logger.info("=" * 60)
        logger.info(f"KẾT THÚC - Best fitness: {self.best_chromosome.fitness:.2f}")
        logger.info(f"Violations: {self.best_chromosome.violations}")
        logger.info("=" * 60)

        return {
            'success': True,
            'best_chromosome': self.best_chromosome,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': generation
        }

    def apply_schedule(self, chromosome: Chromosome) -> List:
        """
        Áp dụng lịch học từ chromosome vào database
        """
        from apps.my_built_in.models.lop_tin_chi import LopTinChi

        scheduled_courses = []

        for gene in chromosome.genes:
            try:
                course = LopTinChi.objects.get(id=gene['course_id'])
                course.teacher_id = gene['teacher_id']
                course.room_id = gene['room_id']
                course.weekday = self.DAYS[gene['day_idx']]
                course.start_period = gene['slot']
                scheduled_courses.append(course)
            except Exception as e:
                logger.error(f"Lỗi khi áp dụng gen {gene}: {str(e)}")

        return scheduled_courses

    def save_to_database(self, chromosome: Chromosome):
        """Lưu lịch học vào database"""
        from django.db import transaction

        try:
            with transaction.atomic():
                scheduled_courses = self.apply_schedule(chromosome)
                for course in scheduled_courses:
                    course.save()

            logger.info(f"✅ Đã lưu {len(scheduled_courses)} lớp vào database")
            return True
        except Exception as e:
            logger.error(f"❌ Lỗi khi lưu database: {str(e)}")
            return False