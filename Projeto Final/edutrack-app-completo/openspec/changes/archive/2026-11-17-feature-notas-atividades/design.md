# Planejamento de notas — não implementado

Entidade candidata: activity_grades(id, activity_id, teacher_id, student_id, grade, max_grade, created_at).
POST /api/activity-grades exigiria professor autorizado para a turma, atividade válida, estudante vinculado, grade >= 0 e grade <= max_grade.
A conta atual student/admin não equivale a um vínculo professor/turma. Criar esse modelo sem definição de autorização seria inseguro.
Decisão: arquivar o exercício de planejamento sem incorporar esses requisitos ao produto implementado.
