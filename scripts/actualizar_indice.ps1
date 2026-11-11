# actualizar_indice.ps1 - PASO 8 (Windows con Microsoft Word instalado)
# Abre el informe generado por generar_informe.py, actualiza el índice y los
# campos (números de página), lo guarda y exporta una copia en PDF.
#   powershell -ExecutionPolicy Bypass -File scripts\actualizar_indice.ps1
param(
    [string]$Docx = (Join-Path $PSScriptRoot "..\informe\Informe_Proyecto_SO_Reemplazo_de_Paginas.docx")
)
$Docx = (Resolve-Path $Docx).Path
$Pdf = [System.IO.Path]::ChangeExtension($Docx, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Docx, $false, $false)
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }   # 2.a pasada: números de página finales
    $doc.Save()
    $doc.ExportAsFixedFormat($Pdf, 17)                            # 17 = PDF
    "Indice actualizado: $Docx"
    "PDF generado: $Pdf ($($doc.ComputeStatistics(2)) paginas)"
    $doc.Close($false)
} finally {
    $word.Quit()
}
