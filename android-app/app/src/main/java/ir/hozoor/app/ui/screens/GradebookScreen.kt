package ir.hozoor.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Add
import androidx.compose.material.icons.rounded.Delete
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.components.ClassCategorySelector
import ir.hozoor.app.ui.components.QuickGradeDialog
import ir.hozoor.app.ui.components.toPersianDigits
import uniffi.hozoor_core.GradeCategory
import uniffi.hozoor_core.StudentGradeRow

/** دفتر نمره کامل: مستمر مهر/آبان/آذر/دی، پودمانی ۱ تا ۵ و امکان ساخت هر عنوان دلخواه توسط معلم */
@Composable
fun GradebookContent(
    majors: List<String>, selectedMajor: String,
    grades: List<String>, selectedGrade: String,
    sections: List<Int>, selectedSection: Int,
    onSelectMajor: (String) -> Unit, onSelectGrade: (String) -> Unit, onSelectSection: (Int) -> Unit,
    categories: List<GradeCategory>,
    selectedCategoryId: Long,
    studentGrades: List<StudentGradeRow>,
    onSelectCategory: (Long) -> Unit,
    onAddCategory: (String) -> Unit,
    onDeleteCategory: (Long) -> Unit,
    onSaveGrade: (studentId: Long, categoryId: Long, score: String, note: String) -> Unit,
    onExportGradebookExcel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var showAddCatDialog by remember { mutableStateOf(false) }
    var editingRow by remember { mutableStateOf<StudentGradeRow?>(null) }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(bottom = 32.dp, top = 2.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        item(key = "gb_cats") {
            ClassCategorySelector(majors, selectedMajor, grades, selectedGrade, sections, selectedSection, onSelectMajor, onSelectGrade, onSelectSection)
        }

        item(key = "gb_header") {
            Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp), shape = RoundedCornerShape(22.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                        Text("عناوین نمره (مستمر، پودمانی، دلخواه)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.ExtraBold, modifier = Modifier.weight(1f))
                        FilledTonalButton(onClick = { showAddCatDialog = true }, contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)) {
                            Icon(Icons.Rounded.Add, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(3.dp)); Text("عنوان جدید")
                        }
                    }

                    LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(categories, key = { it.id }) { cat ->
                            FilterChip(
                                selected = cat.id == selectedCategoryId,
                                onClick = { onSelectCategory(cat.id) },
                                label = { Text(cat.name, fontWeight = if (cat.id == selectedCategoryId) FontWeight.ExtraBold else FontWeight.Medium) }
                            )
                        }
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        OutlinedButton(onClick = onExportGradebookExcel, modifier = Modifier.weight(1f)) {
                            Icon(Icons.Rounded.TableChart, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(5.dp)); Text("خروجی اکسل دفتر نمره")
                        }
                        if (categories.size > 1 && selectedCategoryId > 0) {
                            IconButton(onClick = { onDeleteCategory(selectedCategoryId) }) {
                                Icon(Icons.Rounded.Delete, "حذف این عنوان", tint = MaterialTheme.colorScheme.error)
                            }
                        }
                    }
                }
            }
        }

        itemsIndexed(studentGrades, key = { _, r -> r.studentId }) { idx, row ->
            Surface(
                onClick = { editingRow = row },
                shape = RoundedCornerShape(18.dp),
                color = MaterialTheme.colorScheme.surfaceContainerLow,
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
            ) {
                Row(modifier = Modifier.padding(13.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("${toPersianDigits((idx + 1).toString())}. ${row.firstName} ${row.lastName}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        val sub = buildString {
                            if (row.fatherName.isNotBlank()) append("فرزند ${row.fatherName}")
                            if (row.note.isNotBlank()) { if (isNotEmpty()) append(" • "); append(row.note) }
                        }
                        if (sub.isNotBlank()) Text(sub, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Surface(
                        shape = RoundedCornerShape(14.dp),
                        color = if (row.score.isNotBlank()) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainerHigh
                    ) {
                        Text(
                            text = if (row.score.isNotBlank()) toPersianDigits(row.score) else "ثبت نمره",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.ExtraBold,
                            color = if (row.score.isNotBlank()) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 7.dp)
                        )
                    }
                }
            }
        }
    }

    if (showAddCatDialog) {
        var name by remember { mutableStateOf("") }
        Dialog(onDismissRequest = { showAddCatDialog = false }) {
            Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
                Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("ساخت عنوان نمره جدید", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                    OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("مثلاً مستمر بهمن، پودمان ۶، کوئیز ۱") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedButton(onClick = { showAddCatDialog = false }, modifier = Modifier.weight(1f)) { Text("لغو") }
                        Button(onClick = { onAddCategory(name); showAddCatDialog = false }, modifier = Modifier.weight(1f)) { Text("افزودن") }
                    }
                }
            }
        }
    }

    editingRow?.let { row ->
        QuickGradeDialog(
            studentName = "${row.firstName} ${row.lastName}",
            categories = categories,
            initialCategoryId = selectedCategoryId,
            initialScore = row.score,
            initialNote = row.note,
            onSave = { cid, sc, nt -> onSaveGrade(row.studentId, cid, sc, nt) },
            onDismiss = { editingRow = null }
        )
    }
}
