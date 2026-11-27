package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import uniffi.hozoor_core.StudentAttendanceRow

@Composable
fun StudentEditDialog(
    editingStudent: StudentAttendanceRow?,
    onSave: (first: String, last: String, father: String, nationalId: String, mobile: String) -> Unit,
    onDismiss: () -> Unit
) {
    var first by remember { mutableStateOf(editingStudent?.firstName.orEmpty()) }
    var last by remember { mutableStateOf(editingStudent?.lastName.orEmpty()) }
    var father by remember { mutableStateOf(editingStudent?.fatherName.orEmpty()) }
    var nationalId by remember { mutableStateOf(editingStudent?.nationalId.orEmpty()) }
    var mobile by remember { mutableStateOf(editingStudent?.mobile.orEmpty()) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
            Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = if (editingStudent == null) "افزودن دانش‌آموز جدید" else "ویرایش مشخصات دانش‌آموز",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.ExtraBold
                )
                OutlinedTextField(value = first, onValueChange = { first = it }, label = { Text("نام") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = last, onValueChange = { last = it }, label = { Text("نام خانوادگی") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = father, onValueChange = { father = it }, label = { Text("نام پدر") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = nationalId, onValueChange = { nationalId = it.take(10) }, label = { Text("کد ملی (۱۰ رقم)") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = mobile, onValueChange = { mobile = it }, label = { Text("شماره موبایل") }, singleLine = true, modifier = Modifier.fillMaxWidth())

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("لغو") }
                    Button(
                        onClick = { onSave(first, last, father, nationalId, mobile); onDismiss() },
                        modifier = Modifier.weight(1f)
                    ) { Text("ذخیره") }
                }
            }
        }
    }
}
