package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
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
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.BackupStats
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.PrincipalReportBundle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportAndReportSheet(
    report: PrincipalReportBundle?,
    summary: PeriodSummary,
    backupStats: BackupStats?,
    wholeSchool: Boolean,
    principalPhone: String,
    feedbackMessage: String?,
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
    onSaveBackupToDevice: () -> Unit,
    onShareBackupJson: () -> Unit,
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
            Text("گزارش مدیر، خروجی و پشتیبان کلی", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)

            // پیام راهنما/خطا دقیقاً داخل خود شیت تا هیچ‌وقت پشت صفحه مخفی نشود
            AnimatedVisibility(visible = !feedbackMessage.isNullOrBlank()) {
                Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.errorContainer, modifier = Modifier.fillMaxWidth()) {
                    Text(feedbackMessage.orEmpty(), color = MaterialTheme.colorScheme.onErrorContainer, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold, modifier = Modifier.padding(12.dp))
                }
            }

            OutlinedTextField(
                value = principalPhone,
                onValueChange = onPrincipalPhoneChange,
                label = { Text("شماره موبایل مدیر (برای پیامک عادی)") },
                placeholder = { Text("0917xxxxxxx") },
                leadingIcon = { Icon(Icons.Rounded.Phone, null) },
                singleLine = true,
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = !wholeSchool, onClick = { onToggleWholeSchool(false) }, label = { Text("کلاس فعلی") })
                FilterChip(selected = wholeSchool, onClick = { onToggleWholeSchool(true) }, label = { Text("کل کلاس‌ها") })
                Spacer(Modifier.weight(1f))
                FilterChip(selected = previewSmsMode, onClick = { previewSmsMode = !previewSmsMode }, label = { Text(if (previewSmsMode) "پیامک فشرده" else "متن کامل") })
            }

            // ارسال پیام گروهی همین زنگ (با نمایش تعداد روی دکمه)
            Text("ارسال پیام گروهی همین زنگ به مدیر", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            val absLabel = if (!wholeSchool) " (${toPersianDigits(summary.absent.toString())})" else ""
            val lateLabel = if (!wholeSchool) " (${toPersianDigits(summary.late.toString())})" else ""
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = { onSendGroupPeriodSms(AttendanceStatus.ABSENT) },
                    colors = ButtonDefaults.buttonColors(containerColor = StatusColors.Absent, contentColor = StatusColors.OnAbsent),
                    modifier = Modifier.weight(1f)
                ) { Text("غیبت با پیامک$absLabel", maxLines = 1) }
                FilledTonalButton(onClick = { onSendGroupPeriodShare(AttendanceStatus.ABSENT) }, modifier = Modifier.weight(1f)) {
                    Text("غیبت در پیام‌رسان", maxLines = 1)
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = { onSendGroupPeriodSms(AttendanceStatus.LATE) },
                    colors = ButtonDefaults.buttonColors(containerColor = StatusColors.Late, contentColor = StatusColors.OnLate),
                    modifier = Modifier.weight(1f)
                ) { Text("تأخیر با پیامک$lateLabel", maxLines = 1) }
                OutlinedButton(onClick = { onSendGroupPeriodShare(AttendanceStatus.LATE) }, modifier = Modifier.weight(1f)) {
                    Text("تأخیر در پیام‌رسان", maxLines = 1)
                }
            }

            HorizontalDivider()

            Text("گزارش تجمیعی کل روز (تفکیک کل روز و زنگ‌ها بدون تکرار)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
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
                    Icon(Icons.Rounded.Sms, null); Spacer(Modifier.width(4.dp)); Text("پیامک کل روز")
                }
                FilledTonalButton(onClick = { report?.let { onShareText(it.fullText) } }, enabled = report != null, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Send, null); Spacer(Modifier.width(4.dp)); Text("ارسال متن")
                }
                OutlinedButton(onClick = { onCopyText(previewText) }, enabled = report != null) { Icon(Icons.Rounded.ContentCopy, "کپی") }
            }

            HorizontalDivider()

            Text("خروجی اکسل، CSV و فایل نمونه", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.TableChart, null); Spacer(Modifier.width(4.dp)); Text("اکسل (.xlsx)") }
                OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Description, null); Spacer(Modifier.width(4.dp)); Text("فایل CSV") }
            }
            OutlinedButton(onClick = onExportTemplateExcel, modifier = Modifier.fillMaxWidth()) {
                Icon(Icons.Rounded.Download, null); Spacer(Modifier.width(6.dp)); Text("دریافت فایل نمونه Excel (XLSX)")
            }

            HorizontalDivider()

            Text("پشتیبان‌گیری کلی (دانش‌آموزان، حضور و غیاب، نمرات و تنظیمات)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            if (backupStats != null) {
                Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = "${toPersianDigits(backupStats.studentsCount.toString())} دانش‌آموز • ${toPersianDigits(backupStats.classesCount.toString())} کلاس • ${toPersianDigits(backupStats.attendanceCount.toString())} رکورد حضور و غیاب • ${toPersianDigits(backupStats.scoresCount.toString())} نمره",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(10.dp)
                    )
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onSaveBackupToDevice, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Save, null); Spacer(Modifier.width(4.dp)); Text("ذخیره در گوشی")
                }
                FilledTonalButton(onClick = onShareBackupJson, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Backup, null); Spacer(Modifier.width(4.dp)); Text("ارسال پشتیبان")
                }
            }
            OutlinedButton(onClick = onRestoreBackupJson, modifier = Modifier.fillMaxWidth()) {
                Icon(Icons.Rounded.Restore, null); Spacer(Modifier.width(6.dp)); Text("بازیابی کامل از فایل پشتیبان (JSON)")
            }
        }
    }
}
