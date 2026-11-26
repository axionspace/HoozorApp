package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Phone
import androidx.compose.material.icons.rounded.Send
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
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
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onDismiss: () -> Unit
) {
    var previewSmsMode by remember { mutableStateOf(false) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text("گزارش مدیر و خروجی فایل", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
            Spacer(Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = !wholeSchool, onClick = { onToggleWholeSchool(false) }, label = { Text("کلاس فعلی") })
                FilterChip(selected = wholeSchool, onClick = { onToggleWholeSchool(true) }, label = { Text("کل مدرسه") })
                Spacer(Modifier.weight(1f))
                FilterChip(
                    selected = previewSmsMode,
                    onClick = { previewSmsMode = !previewSmsMode },
                    label = { Text(if (previewSmsMode) "متن پیامک" else "متن پیام‌رسان") }
                )
            }

            Spacer(Modifier.height(10.dp))

            val previewText = when {
                report == null -> "در حال آماده‌سازی گزارش..."
                previewSmsMode -> report.smsText
                else -> report.fullText
            }

            Surface(
                shape = RoundedCornerShape(20.dp),
                color = MaterialTheme.colorScheme.surfaceContainerHigh,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(previewText, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(14.dp))
            }

            Spacer(Modifier.height(12.dp))

            OutlinedTextField(
                value = principalPhone,
                onValueChange = onPrincipalPhoneChange,
                label = { Text("شماره موبایل مدیر (برای ارسال پیامک عادی)") },
                placeholder = { Text("0917xxxxxxx") },
                leadingIcon = { Icon(Icons.Rounded.Phone, contentDescription = null) },
                singleLine = true,
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(Modifier.height(12.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = { report?.let { onSendSms(principalPhone, it.smsText) } },
                    enabled = report != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Rounded.Sms, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("پیامک عادی")
                }
                FilledTonalButton(
                    onClick = { report?.let { onShareText(it.fullText) } },
                    enabled = report != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Rounded.Send, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("ارسال متن")
                }
                OutlinedButton(onClick = { onCopyText(previewText) }, enabled = report != null) {
                    Icon(Icons.Rounded.ContentCopy, contentDescription = "کپی")
                }
            }

            Spacer(Modifier.height(14.dp))
            Text("خروجی فایل روزانه", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(8.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.TableChart, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("فایل اکسل (.xlsx)")
                }
                OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Description, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("فایل CSV")
                }
            }
        }
    }
}
