"""PDF privado em memória; nenhum conteúdo do aluno é tratado como HTML ou URL."""

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from edutrack.progress import calculate_progress


def build_progress_pdf(rows: list[dict], generated_at: datetime) -> bytes:
    """Gera relatório acumulado sem e-mail, CPF, IDs ou dados de outra conta."""
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm,
                            title="EduTrack - Progresso acadêmico", author="EduTrack")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("SmallCell", fontName="Helvetica", fontSize=9, leading=13))
    styles.add(ParagraphStyle("WhiteCell", fontName="Helvetica-Bold", fontSize=9,
                              leading=13, textColor=colors.white))
    styles["Title"].textColor = colors.HexColor("#4338ca")
    total = sum(row["total"] for row in rows)
    done = sum(row["completed"] for row in rows)
    percentage = calculate_progress(done, total)["percentage"]
    story = [Paragraph("EduTrack", styles["Title"]),
             Paragraph("Relatório de progresso acadêmico", styles["Heading2"]),
             Paragraph("Todas as datas · Gerado em " + generated_at.strftime("%d/%m/%Y às %H:%M UTC"), styles["Normal"]),
             Spacer(1, 7 * mm),
             Paragraph(f"<b>{percentage}% concluído</b> · {done} de {total} tarefas elegíveis · {len(rows)} disciplinas", styles["Normal"]),
             Spacer(1, 6 * mm)]
    if rows:
        data = [[Paragraph(title, styles["WhiteCell"]) for title in ("Disciplina", "Concluídas", "Total", "Progresso")]]
        for row in rows:
            data.append([Paragraph(escape(row["name"]), styles["SmallCell"]), str(row["completed"]),
                         str(row["total"]), str(calculate_progress(row["completed"], row["total"])["percentage"]) + "%"])
        table = Table(data, colWidths=[92 * mm, 28 * mm, 22 * mm, 32 * mm], repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338ca")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f3ff"), colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 1), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#312e81")),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Nenhuma disciplina cadastrada. Cadastre um curso e suas disciplinas para começar.", styles["Normal"]))
    story += [Spacer(1, 6 * mm), Paragraph("<b>Como calculamos:</b> tarefas concluídas ÷ total de tarefas não canceladas × 100. "
               "Sem tarefas elegíveis, o progresso é 0%. Percentuais arredondados ao inteiro mais próximo. "
               "O total geral é ponderado pela quantidade de tarefas, não pela média das disciplinas.", styles["SmallCell"])]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(18 * mm, 11 * mm, "EduTrack · Documento pessoal · Progresso acumulado")
        canvas.drawRightString(A4[0] - 18 * mm, 11 * mm, f"Página {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()
