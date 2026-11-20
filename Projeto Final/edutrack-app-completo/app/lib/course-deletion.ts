/** Remove a hierarquia do curso sem apagar o tempo de estudo já registrado. */
export function deleteCourseFromState<
  C extends { id: string },
  D extends { id: string; courseId: string },
  T extends { id: string; courseId: string; disciplineId?: string },
  S extends { taskId?: string },
>(state: { courses: C[]; disciplines: D[]; tasks: T[]; sessions: S[] }, courseId: string) {
  if (!state.courses.some((course) => course.id === courseId)) return state;

  const disciplineIds = new Set(state.disciplines
    .filter((discipline) => discipline.courseId === courseId)
    .map((discipline) => discipline.id));
  const taskIds = new Set(state.tasks
    .filter((task) => task.courseId === courseId || disciplineIds.has(task.disciplineId ?? ''))
    .map((task) => task.id));

  return {
    courses: state.courses.filter((course) => course.id !== courseId),
    disciplines: state.disciplines.filter((discipline) => !disciplineIds.has(discipline.id)),
    tasks: state.tasks.filter((task) => !taskIds.has(task.id)),
    // Desvincula a tarefa excluída, mantendo minutos, datas e demais dados da sessão.
    sessions: state.sessions.map((session) => taskIds.has(session.taskId ?? '')
      ? { ...session, taskId: undefined }
      : session),
  };
}
