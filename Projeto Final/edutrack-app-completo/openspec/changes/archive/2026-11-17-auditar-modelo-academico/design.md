# Correspondência do modelo

subjects → disciplinas: id, name → nome, teacher → professor, hours → carga_horaria, user_id → usuario_id; inclui curso_id.
academic_tasks → tarefas_academicas: title → titulo, description → descricao, due_date → data_prevista, status, subject_id → disciplina_id; inclui usuario_id e auditoria.
UUIDs identificam registros. FKs compostas garantem que curso, disciplina e tarefa pertençam ao mesmo aluno.
status: pendente, em_andamento, concluida, cancelada. Conclusão exige concluido_em. Carga horária e minutos não negativos.
CRUD de disciplinas: GET/POST /api/disciplines; PUT/DELETE /api/disciplines/{id}. PUT preservado por compatibilidade com o cliente existente, em vez do PATCH ilustrativo.
