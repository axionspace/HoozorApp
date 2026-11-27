package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Backup
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Download
import androidx.compose.material.icons.rounded.Phone
import androidx.compose.material.icons.rounded.Restore
import androidx.compose.material.icons.rounded.Send
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
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
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.PrincipalReportBundle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportAndReportSheet(
    report: PrincipalReportBundle?,
    wholeSchool: Boolean,
    principalPhone: String,
    onToggleWholeSchool: (Boolean) -> Unit,
    onPrincipalPhoneChange: (String) -> Unit,
    onSendSms: (phone: String, smsText: String) -> Unit,
    onShareText: (String) -> Unit,
    onCopyText: (String) -> Unit,
    onSendGroupPeriodSms: (AttendanceStatus) -> Unit,
    onSendGroupPeriodShare: (AttendanceStatus) -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onExportTemplateExcel: () -> Unit,
    onExportBackupJson: () -> Unit,
    onRestoreBackupJson: () -> Unit,
    onDismiss: () -> Unit
) {
    var previewSmsMode by remember { mutableStateOf(false) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text("گزارش مدیر، خروجی و پشتیبان‌گیری", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)

            OutlinedTextField(
                value = principalPhone,
                onValueChange = onPrincipalPhoneChange,
                label = { Text("شماره موبایل مدیر (برای پیامک عادی)") },
                placeholder = { Text("0917xxxxxxx") },
                leadingIcon = { Icon(Icons.Rounded.Phone, contentDescription = null) },
                singleLine = true,
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            )

            Text("ارسال پیام گروهی همین زنگ به مدیر", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = { onSendGroupPeriodSms(AttendanceStatus.ABSENT) }, modifier = Modifier.weight(1f)) {
                    Text("غیبت با پیامک")
                }
                FilledTonalButton(onClick = { onSendGroupPeriodShare(AttendanceStatus.ABSENT) }, modifier = Modifier.weight(1f)) {
                    Text("غیبت در پیام‌رسان")
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { onSendGroupPeriodSms(AttendanceStatus.LATE) }, modifier = Modifier.weight(1f)) {
                    Text("تأخیر با پیامک")
                }
                OutlinedButton(onClick = { onSendGroupPeriodShare(AttendanceStatus.LATE) }, modifier = Modifier.weight(1f)) {
                    Text("تأخیر در پیام‌رسان")
                }
            }

            HorizontalDivider()

            Text("گزارش تجمیعی کل روز (بدون تکرار کل روز در زنگ‌ها)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = !wholeSchool, onClick = { onToggleWholeSchool(false) }, label = { Text("کلاس فعلی") })
                FilterChip(selected = wholeSchool, onClick = { onToggleWholeSchool(true) }, label = { Text("کل مدرسه") })
                Spacer(Modifier.weight(1f))
                FilterChip(
                    selected = previewSmsMode,
                    onClick = { previewSmsMode = !previewSmsMode },
                    label = { Text(if (previewSmsMode) "پیامک فشرده" else "متن کامل") }
                )
            }

            val previewText = when {
                report == null -> "در حال آماده‌سازی..."
                previewSmsMode -> report.smsText
                else -> report.fullText
            }

            Surface(shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, modifier = Modifier.fillMaxWidth()) {
                Text(previewText, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(14.dp))
            }

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { report?.let { onSendSms(principalPhone, it.smsText) } }, enabled = report != null, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Sms, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("پیامک عادی")
                }
                FilledTonalButton(onClick = { report?.let { onShareText(it.fullText) } }, enabled = report != null, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Send, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("ارسال متن")
                }
                OutlinedButton(onClick = { onCopyText(previewText) }, enabled = report != null) {
                    Icon(Icons.Rounded.ContentCopy, contentDescription = "کپی")
                }
            }

            HorizontalDivider()

            Text("خروجی اکسل، CSV و فایل نمونه", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.TableChart, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("اکسل (.xlsx)")
                }
                OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Description, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("فایل CSV")
                }
            }
            OutlinedButton(onClick = onExportTemplateExcel, modifier = Modifier.fillMaxWidth()) {
                Icon(Icons.Rounded.Download, contentDescription = null)
                Spacer(Modifier.width(6.dp))
                Text("دریافت فایل نمونه Excel (XLSX)")
            }

            HorizontalDivider()

            Text("پشتیبان‌گیری و بازیابی کامل (JSON)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportBackupJson, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Backup, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("دانلود پشتیبان")
                }
                OutlinedButton(onClick = onRestoreBackupJson, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Restore, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("بازیابی JSON")
                }
            }
        }
    }
}
