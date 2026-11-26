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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Sort
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.MonthlyStudentStat
import java.util.Locale

@Composable
fun MonthlyReportContent(
    report: MonthlyClassReport?,
    sortByAbsence: Boolean,
    onShiftMonth: (Int) -> Unit,
    onToggleSort: () -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    modifier: Modifier = Modifier
) {
    val students = remember(report, sortByAbsence) {
        val list = report?.students.orEmpty()
        if (sortByAbsence) list.sortedByDescending { it.absentPeriods } else list
    }

    Column(modifier = modifier.fillMaxSize()) {
        Surface(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
            shape = RoundedCornerShape(24.dp),
            color = MaterialTheme.colorScheme.surfaceContainerHigh
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    IconButton(onClick = { onShiftMonth(-1) }) {
                        Icon(Icons.Rounded.ChevronRight, contentDescription = "ماه قبل")
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(report?.monthLabel ?: "—", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                        Text(
                            text = "روزهای ثبت‌شده: ${toPersianDigits((report?.recordedDays ?: 0).toString())} روز",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = { onShiftMonth(1) }) {
                        Icon(Icons.Rounded.ChevronLeft, contentDescription = "ماه بعد")
                    }
                }

                Spacer(Modifier.height(10.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                    MonthlyKpi("میانگین حضور", "${toPersianDigits(String.format(Locale.US, "%.1f", report?.averageAttendancePercent ?: 100.0))}٪", StatusColors.Present)
                    MonthlyKpi("غیبت کل روز", toPersianDigits((report?.totalFullAbsentDays ?: 0).toString()), StatusColors.Absent)
                    MonthlyKpi("مجموع زنگ غیبت", toPersianDigits((report?.totalAbsentPeriods ?: 0).toString()), StatusColors.Late)
                }

                Spacer(Modifier.height(12.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                        Icon(Icons.Rounded.TableChart, contentDescription = null)
                        Spacer(Modifier.width(4.dp))
                        Text("اکسل ماهانه")
                    }
                    OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                        Icon(Icons.Rounded.Description, contentDescription = null)
                        Spacer(Modifier.width(4.dp))
                        Text("CSV ماهانه")
                    }
                    FilterChip(selected = sortByAbsence, onClick = onToggleSort, label = { Icon(Icons.Rounded.Sort, contentDescription = "مرتب‌سازی") })
                }
            }
        }

        LazyColumn(modifier = Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 28.dp, top = 4.dp)) {
            itemsIndexed(items = students, key = { _, s -> s.studentId }) { idx, stat ->
                MonthlyStudentCard(index = idx + 1, stat = stat)
            }
        }
    }
}

@Composable
private fun MonthlyKpi(title: String, value: String, color: androidx.compose.ui.graphics.Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(title, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun MonthlyStudentCard(index: Int, stat: MonthlyStudentStat) {
    val pct = (stat.attendancePercent / 100.0).toFloat().coerceIn(0f, 1f)
    val barColor = when {
        stat.attendancePercent >= 90.0 -> StatusColors.Present
        stat.attendancePercent >= 75.0 -> StatusColors.Late
        else -> StatusColors.Absent
    }
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 5.dp),
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "${toPersianDigits(index.toString())}. ${stat.firstName} ${stat.lastName}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                Text(
                    text = "${toPersianDigits(String.format(Locale.US, "%.1f", stat.attendancePercent))}٪",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.ExtraBold,
                    color = barColor
                )
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(progress = { pct }, color = barColor, modifier = Modifier.fillMaxWidth().height(6.dp))
            Spacer(Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("حاضر: ${toPersianDigits(stat.presentPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Present)
                Text("غایب: ${toPersianDigits(stat.absentPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Absent)
                Text("کل روز: ${toPersianDigits(stat.fullAbsentDays.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Absent)
                Text("تأخیر: ${toPersianDigits(stat.latePeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Late)
                Text("موجه: ${toPersianDigits(stat.excusedPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Excused)
            }
        }
    }
}
