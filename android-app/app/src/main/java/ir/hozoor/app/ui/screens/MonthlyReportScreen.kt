package ir.hozoor.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CalendarMonth
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.DeleteSweep
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.Sort
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.components.ClassCategorySelector
import ir.hozoor.app.ui.components.statusLabelFa
import ir.hozoor.app.ui.components.statusOnColor
import ir.hozoor.app.ui.components.statusPrimaryColor
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.util.FileShareHelper
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.ClassAnalytics
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.MonthlyStudentStat
import uniffi.hozoor_core.StudentMonthlyEvent
import uniffi.hozoor_core.TopStudentCount
import java.util.Locale

@Composable
fun MonthlyReportContent(
    majors: List<String>, selectedMajor: String,
    grades: List<String>, selectedGrade: String,
    sections: List<Int>, selectedSection: Int,
    onSelectMajor: (String) -> Unit, onSelectGrade: (String) -> Unit, onSelectSection: (Int) -> Unit,
    analytics: ClassAnalytics?,
    report: MonthlyClassReport?,
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    sortByAbsence: Boolean,
    onShiftMonth: (Int) -> Unit,
    onToggleSort: () -> Unit,
    onInspectStudent: (MonthlyStudentStat) -> Unit,
    inspectingStudent: MonthlyStudentStat?,
    inspectingEvents: List<StudentMonthlyEvent>,
    onDismissInspect: () -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onRequestDeleteClass: () -> Unit,
    modifier: Modifier = Modifier
) {
    val students = remember(report, sortByAbsence, searchQuery) {
        val base = report?.students.orEmpty()
        val q = FileShareHelper.normalizePersianSearch(searchQuery)
        val searched = if (q.isEmpty()) base else base.filter { s ->
            FileShareHelper.normalizePersianSearch("${s.firstName} ${s.lastName} ${s.fatherName} ${s.nationalId}").contains(q)
        }
        if (sortByAbsence) searched.sortedByDescending { it.absentPeriods + it.leftClassPeriods } else searched
    }

    LazyColumn(modifier = modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 36.dp, top = 2.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        item(key = "m_cat") {
            ClassCategorySelector(majors, selectedMajor, grades, selectedGrade, sections, selectedSection, onSelectMajor, onSelectGrade, onSelectSection)
        }

        if (analytics != null) {
            item(key = "m_analytics") {
                Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp), shape = RoundedCornerShape(22.dp), color = MaterialTheme.colorScheme.surfaceContainerLow) {
                    Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("آمار کلی جلسات این کلاس", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold)
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            MonthlyKpi("جلسه", toPersianDigits(analytics.recordedSessions.toString()), MaterialTheme.colorScheme.primary)
                            MonthlyKpi("غایب", toPersianDigits(analytics.totalAbsent.toString()), StatusColors.Absent)
                            MonthlyKpi("تأخیر", toPersianDigits(analytics.totalLate.toString()), StatusColors.Late)
                            MonthlyKpi("غیبت موجه", toPersianDigits(analytics.totalExcused.toString()), StatusColors.Excused)
                            MonthlyKpi("خروج", toPersianDigits(analytics.totalLeftClass.toString()), StatusColors.LeftClass)
                        }
                        HorizontalDivider()
                        TopRankingBox("بیشترین غیبت", analytics.topAbsent, StatusColors.Absent)
                        TopRankingBox("بیشترین خروج از کلاس", analytics.topLeftClass, StatusColors.LeftClass)
                        TopRankingBox("بیشترین تأخیر", analytics.topLate, StatusColors.Late)
                        TopRankingBox("بیشترین غیبت موجه", analytics.topExcused, StatusColors.Excused)
                    }
                }
            }
        }

        item(key = "m_hdr") {
            Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp), shape = RoundedCornerShape(22.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                        IconButton(onClick = { onShiftMonth(-1) }) { Icon(Icons.Rounded.ChevronRight, "ماه قبل") }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(report?.monthLabel ?: "—", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                            Text("روزهای ثبت‌شده: ${toPersianDigits((report?.recordedDays ?: 0).toString())} روز • لمس نام = تاریخ غیبت‌ها", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        IconButton(onClick = { onShiftMonth(1) }) { Icon(Icons.Rounded.ChevronLeft, "ماه بعد") }
                    }
                    Spacer(Modifier.height(10.dp))
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                        MonthlyKpi("میانگین حضور", "${toPersianDigits(String.format(Locale.US, "%.1f", report?.averageAttendancePercent ?: 100.0))}٪", StatusColors.Present)
                        MonthlyKpi("غیبت کل روز", toPersianDigits((report?.totalFullAbsentDays ?: 0).toString()), StatusColors.Absent)
                        MonthlyKpi("خروج از کلاس", toPersianDigits((report?.totalLeftClass ?: 0).toString()), StatusColors.LeftClass)
                    }
                    Spacer(Modifier.height(12.dp))
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.TableChart, null); Spacer(Modifier.width(4.dp)); Text("اکسل ماهانه") }
                        OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) { Icon(Icons.Rounded.Description, null); Spacer(Modifier.width(4.dp)); Text("CSV ماهانه") }
                        FilterChip(selected = sortByAbsence, onClick = onToggleSort, label = { Icon(Icons.Rounded.Sort, "مرتب‌سازی") })
                    }
                }
            }
        }

        // باکس جستجو در آمار و گزارش ماهانه
        item(key = "m_search") {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = onSearchChange,
                placeholder = { Text("جستجوی دانش‌آموز در گزارش ماهانه...") },
                leadingIcon = { Icon(Icons.Rounded.Search, null) },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { onSearchChange("") }) { Icon(Icons.Rounded.Close, "پاک کردن") }
                    }
                },
                singleLine = true,
                shape = RoundedCornerShape(22.dp),
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
            )
        }

        itemsIndexed(students, key = { _, s -> s.studentId }) { idx, stat ->
            MonthlyStudentCard(index = idx + 1, stat = stat, onClick = { onInspectStudent(stat) })
        }

        item(key = "m_del") {
            OutlinedButton(
                onClick = onRequestDeleteClass,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error),
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)
            ) { Icon(Icons.Rounded.DeleteSweep, null); Spacer(Modifier.width(6.dp)); Text("حذف کامل این کلاس و سوابقش") }
        }
    }

    // باکس نمایش تاریخ دقیق غیبت‌ها، تأخیرها، غیبت‌های موجه و خروج‌های دانش‌آموز در ماه انتخاب‌شده
    if (inspectingStudent != null) {
        StudentMonthlyDetailsDialog(
            student = inspectingStudent,
            monthLabel = report?.monthLabel.orEmpty(),
            events = inspectingEvents,
            onDismiss = onDismissInspect
        )
    }
}

@Composable
private fun StudentMonthlyDetailsDialog(
    student: MonthlyStudentStat,
    monthLabel: String,
    events: List<StudentMonthlyEvent>,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(28.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, tonalElevation = 8.dp) {
            Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.CalendarMonth, null, tint = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.width(8.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("${student.firstName} ${student.lastName}", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                        Text("تاریخچه غیبت‌ها و تأخیرها در $monthLabel", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                }

                // خلاصه سریع
                Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth()) {
                    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp, horizontal = 10.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                        MonthlyKpi("غایب", toPersianDigits(student.absentPeriods.toString()), StatusColors.Absent)
                        MonthlyKpi("تأخیر", toPersianDigits(student.latePeriods.toString()), StatusColors.Late)
                        MonthlyKpi("غیبت موجه", toPersianDigits(student.excusedPeriods.toString()), StatusColors.Excused)
                        MonthlyKpi("خروج", toPersianDigits(student.leftClassPeriods.toString()), StatusColors.LeftClass)
                    }
                }

                if (events.isEmpty()) {
                    Surface(shape = RoundedCornerShape(16.dp), color = StatusColors.Present.copy(alpha = 0.14f), modifier = Modifier.fillMaxWidth()) {
                        Row(modifier = Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Rounded.CheckCircle, null, tint = StatusColors.Present)
                            Spacer(Modifier.width(8.dp))
                            Text("در $monthLabel هیچ غیبت، تأخیر یا خروجی برای این دانش‌آموز ثبت نشده است.", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
                        }
                    }
                } else {
                    LazyColumn(modifier = Modifier.fillMaxWidth().heightIn(max = 320.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(events) { ev ->
                            val stColor = statusPrimaryColor(ev.status)
                            Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surfaceContainerLow, modifier = Modifier.fillMaxWidth()) {
                                Row(modifier = Modifier.padding(11.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(ev.jalaliDate, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.ExtraBold)
                                        val detail = buildString {
                                            append(ev.periodLabel)
                                            if (ev.eventTime.isNotBlank()) append(" • ساعت ${toPersianDigits(ev.eventTime)}")
                                            if (ev.note.isNotBlank()) append(" • ${ev.note}")
                                        }
                                        Text(detail, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    }
                                    Surface(shape = RoundedCornerShape(12.dp), color = stColor) {
                                        Text(
                                            text = statusLabelFa(ev.status),
                                            style = MaterialTheme.typography.labelSmall,
                                            fontWeight = FontWeight.ExtraBold,
                                            color = statusOnColor(ev.status),
                                            modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                Button(onClick = onDismiss, modifier = Modifier.fillMaxWidth()) { Text("بستن") }
            }
        }
    }
}

@Composable
private fun TopRankingBox(title: String, items: List<TopStudentCount>, accent: Color) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(title, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.ExtraBold, color = accent)
        if (items.isEmpty()) Text("موردی نیست.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        else items.forEachIndexed { i, r ->
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("${toPersianDigits((i + 1).toString())}. ${r.fullName}", style = MaterialTheme.typography.bodyMedium)
                Text("${toPersianDigits(r.count.toString())} مورد", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = accent)
            }
        }
    }
}

@Composable
private fun MonthlyKpi(title: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(title, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun MonthlyStudentCard(index: Int, stat: MonthlyStudentStat, onClick: () -> Unit) {
    val pct = (stat.attendancePercent / 100.0).toFloat().coerceIn(0f, 1f)
    val bc = when { stat.attendancePercent >= 90.0 -> StatusColors.Present; stat.attendancePercent >= 75.0 -> StatusColors.Late; else -> StatusColors.Absent }
    Surface(onClick = onClick, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp), shape = RoundedCornerShape(20.dp), color = MaterialTheme.colorScheme.surfaceContainerLow) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("${toPersianDigits(index.toString())}. ${stat.firstName} ${stat.lastName}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                Text("${toPersianDigits(String.format(Locale.US, "%.1f", stat.attendancePercent))}٪", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.ExtraBold, color = bc)
                Spacer(Modifier.width(4.dp))
                Icon(Icons.Rounded.ChevronLeft, "مشاهده تاریخ‌ها", tint = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.size(18.dp))
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(progress = { pct }, color = bc, modifier = Modifier.fillMaxWidth().height(6.dp))
            Spacer(Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("حاضر:${toPersianDigits(stat.presentPeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.Present)
                Text("غایب:${toPersianDigits(stat.absentPeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.Absent)
                Text("تأخیر:${toPersianDigits(stat.latePeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.Late)
                Text("موجه:${toPersianDigits(stat.excusedPeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.Excused)
                Text("خروج:${toPersianDigits(stat.leftClassPeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.LeftClass)
            }
        }
    }
}
