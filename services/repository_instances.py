from models.repository.repository import Repository
from models.repository.aspirante_repository import AspiranteRepository
from models.repository.professor_repository import ProfessorRepository
from models.repository.turma_repository import TurmaRepository
from models.repository.encontro_repository import EncontroRepository
from models.repository.atividade_repository import AtividadeRepository
from models.repository.evento_repository import EventoRepository

# Criando uma conexão única com o banco de dados
repository = Repository()
aspirante_repo = AspiranteRepository(repository)
professor_repo = ProfessorRepository(repository)
turma_repo = TurmaRepository(repository)
encontro_repo = EncontroRepository(repository)
atividades_repo = AtividadeRepository(repository)
eventos_repo = EventoRepository(repository)