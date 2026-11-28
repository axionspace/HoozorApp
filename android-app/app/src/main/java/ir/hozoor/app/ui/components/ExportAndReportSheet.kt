package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Backup
import androidx.compose.material.icons.rounded.BookmarkAdd
import androidx.compose.material.icons.rounded.Chat
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Contacts
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Download
import androidx.compose.material.icons.rounded.Grade
import androidx.compose.material.icons.rounded.Phone
import androidx.compose.material.icons.rounded.Restore
import androidx.compose.material.icons.rounded.Save
import androidx.compose.material.icons.rounded.Send
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.InputChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.BackupStats
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.PrincipalReportBundle
import uniffi.hozoor_core.SavedContact
import uniffi.hozoor_core.StudentAttendanceRow

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportAndReportSheet(
    report: PrincipalReportBundle?,
    summary: PeriodSummary,
    students: List<StudentAttendanceRow>,
    savedContacts: List<SavedContact>,
    backupStats: BackupStats?,
    wholeSchool: Boolean,
    recipientName: String,
    recipientPhone: String,
    feedbackMessage: String?,
    onToggleWholeSchool: (Boolean) -> Unit,
    onRecipientPhoneChange: (String) -> Unit,
    onPickPhoneContact: () -> Unit,
    onSelectSavedContact: (SavedContact) -> Unit,
    onSaveCurrentContact: (String, String) -> Unit,
    onDeleteSavedContact: (Long) -> Unit,
    onLoadPeriodGroupMessage: (AttendanceStatus, (String) -> Unit) -> Unit,
    onSendSms: (String, String) -> Unit,
    onSendWhatsApp: (String, String) -> Unit,
    onShareText: (String) -> Unit,
    onCopyText: (String) -> Unit,
    onNotifyParentSms: (StudentAttendanceRow) -> Unit,
    onNotifyParentWhatsApp: (StudentAttendanceRow) -> Unit,
    onExportDailyExcel: () -> Unit,
    onExportGradebookExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onExportTemplateExcel: () -> Unit,
    onSaveBackupToDevice: () -> Unit,
    onShareBackupJson: () -> Unit,
    onRestoreBackupJson: () -> Unit,
    onDismiss: () -> Unit
) {
    var msgMode by remember { mutableIntStateOf(0) }
    var editableText by remember { mutableStateOf("") }
    var contactLabel by remember(recipientName) { mutableStateOf(recipientName.ifBlank { "مدیر" }) }

    LaunchedEffect(report, msgMode) {
        when (msgMode) {
            0 -> editableText = report?.fullText.orEmpty()
            1 -> editableText = report?.smsText.orEmpty()
        }
    }

    val flaggedStudents = remember(students) {
        students.filter { it.currentStatus in listOf(AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.LEFT_CLASS) && it.mobile.isNotBlank() }
    }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 18.dp).padding(bottom = 28.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text("مرکز ارسال، مخاطبین و خروجی", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)

            AnimatedVisibility(visible = !feedbackMessage.isNullOrBlank()) {
                Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.errorContainer, modifier = Modifier.fillMaxWidth()) {
                    Text(feedbackMessage.orEmpty(), color = MaterialTheme.colorScheme.onErrorContainer, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold, modifier = Modifier.padding(10.dp))
                }
            }

            Surface(shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("گیرنده پیام", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.ExtraBold, modifier = Modifier.weight(1f))
                        FilledTonalButton(onClick = onPickPhoneContact, contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)) {
                            Icon(Icons.Rounded.Contacts, null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(5.dp))
                            Text("از مخاطبین گوشی", style = MaterialTheme.typography.labelMedium)
                        }
                    }

                    if (savedContacts.isNotEmpty()) {
                        LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            items(savedContacts, key = { it.id }) { c ->
                                InputChip(
                                    selected = c.phone == recipientPhone,
                                    onClick = { onSelectSavedContact(c) },
                                    label = { Text("${c.name} (${toPersianDigits(c.phone.takeLast(4))})") },
                                    trailingIcon = {
                                        IconButton(onClick = { onDeleteSavedContact(c.id) }, modifier = Modifier.size(18.dp)) {
                                            Icon(Icons.Rounded.Close, "حذف", modifier = Modifier.size(14.dp))
                                        }
                                    }
                                )
                            }
                        }
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                        OutlinedTextField(value = recipientPhone, onValueChange = onRecipientPhoneChange, label = { Text("شماره گیرنده") }, placeholder = { Text("0917xxxxxxx") }, leadingIcon = { Icon(Icons.Rounded.Phone, null) }, singleLine = true, shape = RoundedCornerShape(14.dp), modifier = Modifier.weight(1.3f))
                        OutlinedTextField(value = contactLabel, onValueChange = { contactLabel = it }, label = { Text("نام") }, singleLine = true, shape = RoundedCornerShape(14.dp), modifier = Modifier.weight(0.8f))
                        IconButton(onClick = { onSaveCurrentContact(contactLabel, recipientPhone) }) {
                            Icon(Icons.Rounded.BookmarkAdd, "ذخیره مخاطب", tint = MaterialTheme.colorScheme.primary)
                        }
                    }
                }
            }

            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                FilterChip(selected = !wholeSchool, onClick = { onToggleWholeSchool(false); msgMode = 0 }, label = { Text("کلاس فعلی") })
                FilterChip(selected = wholeSchool, onClick = { onToggleWholeSchool(true); msgMode = 0 }, label = { Text("کل کلاس‌ها") })
            }

            LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                item { FilterChip(selected = msgMode == 0, onClick = { msgMode = 0 }, label = { Text("گزارش کامل روز") }) }
                item { FilterChip(selected = msgMode == 1, onClick = { msgMode = 1 }, label = { Text("پیامک فشرده روز") }) }
                item { FilterChip(selected = msgMode == 2, onClick = { onLoadPeriodGroupMessage(AttendanceStatus.ABSENT) { msgMode = 2; editableText = it } }, label = { Text("غیبت این زنگ (${toPersianDigits(summary.absent.toString())})") }) }
                item { FilterChip(selected = msgMode == 3, onClick = { onLoadPeriodGroupMessage(AttendanceStatus.LATE) { msgMode = 3; editableText = it } }, label = { Text("تأخیر (${toPersianDigits(summary.late.toString())})") }) }
                item { FilterChip(selected = msgMode == 4, onClick = { onLoadPeriodGroupMessage(AttendanceStatus.LEFT_CLASS) { msgMode = 4; editableText = it } }, label = { Text("خروج از کلاس (${toPersianDigits(summary.leftClass.toString())})") }) }
            }

            OutlinedTextField(value = editableText, onValueChange = { editableText = it }, label = { Text("متن آماده ارسال (قابل ویرایش دستی)") }, minLines = 4, maxLines = 9, shape = RoundedCornerShape(18.dp), modifier = Modifier.fillMaxWidth())

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Button(onClick = { onSendSms(recipientPhone, editableText) }, enabled = editableText.isNotBlank(), modifier = Modifier.weight(1f), contentPadding = PaddingValues(horizontal = 6.dp, vertical = 10.dp)) {
                    Icon(Icons.Rounded.Sms, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("پیامک عادی", maxLines = 1)
                }
                Button(onClick = { onSendWhatsApp(recipientPhone, editableText) }, enabled = editableText.isNotBlank(), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF16A34A), contentColor = Color.White), modifier = Modifier.weight(1f), contentPadding = PaddingValues(horizontal = 6.dp, vertical = 10.dp)) {
                    Icon(Icons.Rounded.Chat, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("واتساپ", maxLines = 1)
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                FilledTonalButton(onClick = { onShareText(editableText) }, enabled = editableText.isNotBlank(), modifier = Modifier.weight(1.3f)) {
                    Icon(Icons.Rounded.Send, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(5.dp)); Text("شاد / ایتا / بله / سایر")
                }
                OutlinedButton(onClick = { onCopyText(editableText) }, enabled = editableText.isNotBlank(), modifier = Modifier.weight(0.7f)) {
                    Icon(Icons.Rounded.ContentCopy, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("کپی")
                }
            }

            if (flaggedStudents.isNotEmpty()) {
                HorizontalDivider()
                Text("اطلاع‌رسانی مستقیم به اولیا (${toPersianDigits(flaggedStudents.size.toString())} نفر)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.ExtraBold)
                flaggedStudents.forEach { st ->
                    Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surfaceContainerLow, modifier = Modifier.fillMaxWidth()) {
                        Row(modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text("${st.firstName} ${st.lastName}", style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                                val subtitle = when {
                                    st.currentStatus == AttendanceStatus.LEFT_CLASS && st.eventTime.isNotBlank() -> "خروج ساعت ${toPersianDigits(st.eventTime)}"
                                    st.currentStatus == AttendanceStatus.LATE && st.eventTime.isNotBlank() -> "تأخیر ساعت ${toPersianDigits(st.eventTime)}"
                                    else -> statusLabelFa(st.currentStatus)
                                }
                                Text(subtitle, style = MaterialTheme.typography.labelSmall, color = statusPrimaryColor(st.currentStatus))
                            }
                            IconButton(onClick = { onNotifyParentSms(st) }) { Icon(Icons.Rounded.Sms, "پیامک ولی", tint = MaterialTheme.colorScheme.primary) }
                            IconButton(onClick = { onNotifyParentWhatsApp(st) }) { Icon(Icons.Rounded.Chat, "واتساپ ولی", tint = Color(0xFF16A34A)) }
                        }
                    }
                }
            }

            HorizontalDivider()
            Text("خروجی اکسل و CSV", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportDailyExcel, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.TableChart, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("اکسل حضور") }
                FilledTonalButton(onClick = onExportGradebookExcel, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Grade, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("اکسل نمرات") }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Description, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("فایل CSV") }
                OutlinedButton(onClick = onExportTemplateExcel, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Download, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("نمونه اکسل") }
            }

            HorizontalDivider()
            Text("پشتیبان‌گیری کلی", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            if (backupStats != null) {
                Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = "${toPersianDigits(backupStats.studentsCount.toString())} دانش‌آموز • ${toPersianDigits(backupStats.attendanceCount.toString())} حضور • ${toPersianDigits(backupStats.gradesCount.toString())} نمره • ${toPersianDigits(backupStats.contactsCount.toString())} مخاطب",
                        style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(10.dp)
                    )
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onSaveBackupToDevice, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Save, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("ذخیره در گوشی") }
                FilledTonalButton(onClick = onShareBackupJson, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Backup, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text("ارسال پشتیبان") }
            }
            OutlinedButton(onClick = onRestoreBackupJson, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Rounded.Restore, null); Spacer(Modifier.width(6.dp)); Text("بازیابی کامل از پشتیبان JSON") }
        }
    }
}

fun statusLabelFa(st: AttendanceStatus): String = when (st) {
    AttendanceStatus.ABSENT -> "غایب"
    AttendanceStatus.LATE -> "تأخیر"
    AttendanceStatus.EXCUSED -> "غیبت موجه"
    AttendanceStatus.LEFT_CLASS -> "خروج از کلاس"
    else -> "حاضر"
}
