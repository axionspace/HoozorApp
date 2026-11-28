from pathlib import Path

STALE_FILES = [
    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExitTimeWheelDialog.kt",
]

FILES = {
    "android-app/app/src/main/java/ir/hozoor/app/ui/components/PeriodSelector.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.NotificationsActive
import androidx.compose.material3.ButtonGroupDefaults
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.ToggleButton
import androidx.compose.material3.ToggleButtonDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import uniffi.hozoor_core.Period

private val ALL_PERIODS = listOf(
    Period.FIRST to "زنگ ۱",
    Period.SECOND to "زنگ ۲",
    Period.THIRD to "زنگ ۳",
    Period.FOURTH to "زنگ ۴"
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun PeriodSelector(selectedPeriod: Period, onSelectPeriod: (Period) -> Unit, modifier: Modifier = Modifier) {
    val haptic = LocalHapticFeedback.current
    Row(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(ButtonGroupDefaults.ConnectedSpaceBetween)
    ) {
        ALL_PERIODS.forEachIndexed { index, (period, label) ->
            val checked = selectedPeriod == period
            val shapes = when (index) {
                0 -> ButtonGroupDefaults.connectedLeadingButtonShapes()
                ALL_PERIODS.lastIndex -> ButtonGroupDefaults.connectedTrailingButtonShapes()
                else -> ButtonGroupDefaults.connectedMiddleButtonShapes()
            }
            ToggleButton(
                checked = checked,
                onCheckedChange = { haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove); onSelectPeriod(period) },
                modifier = Modifier.weight(1f),
                shapes = shapes,
                contentPadding = PaddingValues(horizontal = 4.dp, vertical = 8.dp),
                colors = ToggleButtonDefaults.toggleButtonColors(
                    checkedContainerColor = MaterialTheme.colorScheme.primary,
                    checkedContentColor = MaterialTheme.colorScheme.onPrimary,
                    containerColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                    contentColor = MaterialTheme.colorScheme.onSurface
                )
            ) {
                if (checked) {
                    Icon(Icons.Rounded.NotificationsActive, null, modifier = Modifier.size(14.dp))
                    Spacer(Modifier.width(2.dp))
                }
                Text(label, style = MaterialTheme.typography.labelMedium, fontWeight = if (checked) FontWeight.ExtraBold else FontWeight.SemiBold, maxLines = 1, softWrap = false)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ClassCategorySelector.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

@Composable
fun ClassCategorySelector(
    majors: List<String>, selectedMajor: String,
    grades: List<String>, selectedGrade: String,
    sections: List<Int>, selectedSection: Int,
    onSelectMajor: (String) -> Unit, onSelectGrade: (String) -> Unit, onSelectSection: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            if (majors.isNotEmpty()) {
                AnimatedCategoryGrid("رشته", majors, selectedMajor, { it }, 52.dp, 2, MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.onPrimary, MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.48f), MaterialTheme.colorScheme.onSurface, onSelectMajor)
            }
            if (grades.isNotEmpty()) {
                AnimatedCategoryGrid("پایه", grades, selectedGrade, { it }, 44.dp, 1, MaterialTheme.colorScheme.secondary, MaterialTheme.colorScheme.onSecondary, MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f), MaterialTheme.colorScheme.onSurface, onSelectGrade)
            }
            if (sections.isNotEmpty()) {
                AnimatedCategoryGrid("شعبه", sections, selectedSection, { "شعبه ${toPersianDigits(it.toString())}" }, 42.dp, 1, MaterialTheme.colorScheme.tertiary, MaterialTheme.colorScheme.onTertiary, MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.55f), MaterialTheme.colorScheme.onSurface, onSelectSection)
            }
        }
    }
}

@Composable
private fun <T> AnimatedCategoryGrid(
    title: String, items: List<T>, selected: T, labelOf: (T) -> String,
    itemHeight: Dp, maxLines: Int, selBg: Color, selFg: Color, unselBg: Color, unselFg: Color, onSelect: (T) -> Unit
) {
    val haptic = LocalHapticFeedback.current
    Column {
        Text(title, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 5.dp, start = 2.dp))
        Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
            items.chunked(3).forEach { chunk ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    chunk.forEach { item ->
                        val isSel = item == selected
                        val bg by animateColorAsState(if (isSel) selBg else unselBg, spring(stiffness = Spring.StiffnessMediumLow), label = "cBg")
                        val fg by animateColorAsState(if (isSel) selFg else unselFg, spring(stiffness = Spring.StiffnessMediumLow), label = "cFg")
                        val corner by animateDpAsState(if (isSel) 22.dp else 13.dp, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "cCr")
                        val scale by animateFloatAsState(if (isSel) 1.03f else 0.98f, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "cSc")
                        Surface(
                            onClick = { haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove); onSelect(item) },
                            shape = RoundedCornerShape(corner), color = bg, shadowElevation = if (isSel) 3.dp else 0.dp,
                            modifier = Modifier.weight(1f).height(itemHeight).graphicsLayer { scaleX = scale; scaleY = scale }
                        ) {
                            Box(contentAlignment = Alignment.Center, modifier = Modifier.fillMaxSize().padding(horizontal = 6.dp, vertical = 4.dp)) {
                                Text(labelOf(item), style = MaterialTheme.typography.labelLarge, fontWeight = if (isSel) FontWeight.ExtraBold else FontWeight.SemiBold, color = fg, maxLines = maxLines, textAlign = TextAlign.Center)
                            }
                        }
                    }
                    repeat(3 - chunk.size) { Spacer(Modifier.weight(1f)) }
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/TimeWheelDialog.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.snapping.rememberSnapFlingBehavior
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AccessTimeFilled
import androidx.compose.material.icons.rounded.DirectionsRun
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.MyLocation
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.util.FileShareHelper
import kotlinx.coroutines.launch
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.StudentAttendanceRow
import java.time.LocalTime

private val LATE_PRESET_MINUTES = listOf(5, 10, 15, 20, 30)
private val LATE_REASONS = listOf("ترافیک / سرویس", "خواب ماندن", "هماهنگ با دفتر", "تأخیر غیرموجه")
private val EXIT_REASONS = listOf("برنگشت", "با اجازه", "دفتر / معاون", "بهداشت / آبخوری")

/**
 * دیالوگ مدرن انتخاب زمان:
 * - برای «تأخیر»: انتخاب مدت تأخیر به دقیقه (۱ تا ۱۲۰ دقیقه) + چیپ‌های ۵، ۱۰، ۱۵، ۲۰، ۳۰ دقیقه + تایپ دستی با لمس عدد بالا
 * - برای «خروج از کلاس»: چرخ ساعت و دقیقه (پیش‌فرض ساعت گوشی) با علامت `:` کاملاً وسط + تایپ دستی با لمس عدد بالا
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun TimeWheelDialog(
    student: StudentAttendanceRow,
    targetStatus: AttendanceStatus,
    onConfirm: (value: String, reason: String) -> Unit,
    onDismiss: () -> Unit
) {
    val isLate = targetStatus == AttendanceStatus.LATE
    val accent = if (isLate) StatusColors.Late else StatusColors.LeftClass
    val onAccent = if (isLate) StatusColors.OnLate else StatusColors.OnLeftClass
    val title = if (isLate) "ثبت مدت تأخیر (دقیقه)" else "ثبت ساعت خروج از کلاس"
    val reasons = if (isLate) LATE_REASONS else EXIT_REASONS
    val defaultReason = if (isLate) "" else "برنگشت"

    val scope = rememberCoroutineScope()
    val now = remember { LocalTime.now() }

    // حالت تأخیر: دقیقه ۱..۱۲۰ (پیش‌فرض ۱۰ دقیقه)
    val initLateMinutes = remember(student.eventTime, targetStatus) {
        if (isLate && student.currentStatus == AttendanceStatus.LATE) {
            student.eventTime.filter { it.isDigit() }.toIntOrNull()?.coerceIn(1, 120) ?: 10
        } else 10
    }
    var selectedLateMin by remember { mutableIntStateOf(initLateMinutes) }
    val lateWheelState = rememberLazyListState(initialFirstVisibleItemIndex = (initLateMinutes - 1).coerceIn(0, 119))

    // حالت خروج: ساعت و دقیقه روی ساعت گوشی
    val initClock = remember(student.eventTime, targetStatus) {
        val useSaved = !isLate && student.currentStatus == AttendanceStatus.LEFT_CLASS && student.eventTime.contains(":")
        val sp = if (useSaved) student.eventTime.split(":") else emptyList()
        val h = sp.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: now.hour
        val m = sp.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: now.minute
        h to m
    }
    var selectedHour by remember { mutableIntStateOf(initClock.first) }
    var selectedMinute by remember { mutableIntStateOf(initClock.second) }
    val hourState = rememberLazyListState(initialFirstVisibleItemIndex = initClock.first)
    val minState = rememberLazyListState(initialFirstVisibleItemIndex = initClock.second)

    var note by remember { mutableStateOf(if (student.currentStatus == targetStatus) student.note else defaultReason) }
    var showManualInput by remember { mutableStateOf(false) }
    var manualMinText by remember { mutableStateOf(initLateMinutes.toString()) }
    var manualHourText by remember { mutableStateOf(String.format("%02d", initClock.first)) }
    var manualClockMinText by remember { mutableStateOf(String.format("%02d", initClock.second)) }

    val formattedClock = String.format("%02d:%02d", selectedHour, selectedMinute)
    val itemH = 44.dp
    val wheelBg = MaterialTheme.colorScheme.surfaceContainerLowest

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(30.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, tonalElevation = 8.dp) {
            Column(modifier = Modifier.padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                    Surface(shape = CircleShape, color = accent.copy(alpha = 0.18f), modifier = Modifier.size(42.dp)) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(if (isLate) Icons.Rounded.Schedule else Icons.Rounded.DirectionsRun, null, tint = accent, modifier = Modifier.size(22.dp))
                        }
                    }
                    Spacer(Modifier.width(10.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold)
                        Text("${student.firstName} ${student.lastName}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    if (!isLate) {
                        TextButton(
                            onClick = {
                                val cur = LocalTime.now()
                                scope.launch {
                                    hourState.animateScrollToItem(cur.hour)
                                    minState.animateScrollToItem(cur.minute)
                                }
                            },
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Icon(Icons.Rounded.MyLocation, null, modifier = Modifier.size(14.dp))
                            Spacer(Modifier.width(3.dp))
                            Text("الان", style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        }
                    }
                }

                Spacer(Modifier.height(10.dp))

                // عدد بزرگ بالا: قابل لمس برای وارد کردن دستی زمان!
                Surface(
                    onClick = {
                        manualMinText = selectedLateMin.toString()
                        manualHourText = String.format("%02d", selectedHour)
                        manualClockMinText = String.format("%02d", selectedMinute)
                        showManualInput = !showManualInput
                    },
                    shape = RoundedCornerShape(20.dp),
                    color = accent.copy(alpha = 0.15f),
                    border = BorderStroke(1.5.dp, accent.copy(alpha = 0.55f))
                ) {
                    Row(modifier = Modifier.padding(horizontal = 16.dp, vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.AccessTimeFilled, null, tint = accent, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text(
                            text = if (isLate) "${toPersianDigits(selectedLateMin.toString())} دقیقه تأخیر" else toPersianDigits(formattedClock),
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Spacer(Modifier.width(8.dp))
                        Icon(Icons.Rounded.Edit, "ورود دستی", tint = accent, modifier = Modifier.size(16.dp))
                    }
                }
                Text("برای وارد کردن دستی، روی عدد بالا بزنید", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 3.dp))

                // باکس ورود دستی زمان (بازشو با لمس عدد بالا)
                AnimatedVisibility(visible = showManualInput) {
                    Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth().padding(top = 8.dp)) {
                        if (isLate) {
                            Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(
                                    value = manualMinText,
                                    onValueChange = { manualMinText = FileShareHelper.normalizePersianSearch(it).filter { c -> c.isDigit() }.take(3) },
                                    label = { Text("دقیقه (۱ تا ۱۲۰)") },
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                    modifier = Modifier.weight(1f)
                                )
                                FilledTonalButton(onClick = {
                                    val m = manualMinText.toIntOrNull()?.coerceIn(1, 120) ?: selectedLateMin
                                    selectedLateMin = m
                                    showManualInput = false
                                    scope.launch { lateWheelState.animateScrollToItem((m - 1).coerceIn(0, 119)) }
                                }) { Text("اعمال") }
                            }
                        } else {
                            CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
                                Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    OutlinedTextField(
                                        value = manualHourText,
                                        onValueChange = { manualHourText = FileShareHelper.normalizePersianSearch(it).filter { c -> c.isDigit() }.take(2) },
                                        label = { Text("ساعت") }, singleLine = true,
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                        modifier = Modifier.weight(1f)
                                    )
                                    Text(":", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                                    OutlinedTextField(
                                        value = manualClockMinText,
                                        onValueChange = { manualClockMinText = FileShareHelper.normalizePersianSearch(it).filter { c -> c.isDigit() }.take(2) },
                                        label = { Text("دقیقه") }, singleLine = true,
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                        modifier = Modifier.weight(1f)
                                    )
                                    FilledTonalButton(onClick = {
                                        val h = manualHourText.toIntOrNull()?.coerceIn(0, 23) ?: selectedHour
                                        val m = manualClockMinText.toIntOrNull()?.coerceIn(0, 59) ?: selectedMinute
                                        selectedHour = h; selectedMinute = m; showManualInput = false
                                        scope.launch { hourState.animateScrollToItem(h); minState.animateScrollToItem(m) }
                                    }) { Text("اعمال") }
                                }
                            }
                        }
                    }
                }

                Spacer(Modifier.height(10.dp))

                // چرخ اسکرول مدرن (دقیقه‌ای برای تأخیر | ساعت:دقیقه با تراز دقیق `:` برای خروج)
                Surface(
                    shape = RoundedCornerShape(24.dp),
                    color = wheelBg,
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    if (isLate) {
                        Column(modifier = Modifier.fillMaxWidth().padding(vertical = 10.dp, horizontal = 12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                            // انتخاب سریع ۵، ۱۰، ۱۵، ۲۰، ۳۰ دقیقه
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                LATE_PRESET_MINUTES.forEach { preset ->
                                    FilterChip(
                                        selected = selectedLateMin == preset,
                                        onClick = {
                                            selectedLateMin = preset
                                            scope.launch { lateWheelState.animateScrollToItem(preset - 1) }
                                        },
                                        label = { Text(toPersianDigits(preset.toString()), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold) },
                                        modifier = Modifier.weight(1f)
                                    )
                                }
                            }
                            Spacer(Modifier.height(6.dp))
                            ExpressiveWheelColumn(
                                count = 120,
                                startFrom = 1,
                                listState = lateWheelState,
                                itemH = itemH,
                                wheelWidth = 150.dp,
                                accent = accent,
                                fadeBg = wheelBg,
                                formatValue = { "${toPersianDigits(it.toString())} دقیقه" },
                                onValueChange = { selectedLateMin = it }
                            )
                        }
                    } else {
                        // ردیف عنوان‌ها کاملاً جدا بالای چرخ‌ها تا علامت `:` در ردیف چرخ‌ها دقیقاً وسط باشد
                        Column(modifier = Modifier.fillMaxWidth().padding(vertical = 10.dp, horizontal = 12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                            CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                                    Text("ساعت", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.width(90.dp))
                                    Spacer(Modifier.width(28.dp))
                                    Text("دقیقه", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.width(90.dp))
                                }
                                Spacer(Modifier.height(4.dp))
                                Row(
                                    modifier = Modifier.fillMaxWidth().height(itemH * 3),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Center
                                ) {
                                    ExpressiveWheelColumn(24, 0, hourState, itemH, 90.dp, accent, wheelBg, { toPersianDigits(String.format("%02d", it)) }) { selectedHour = it }
                                    Box(modifier = Modifier.width(28.dp).height(itemH * 3), contentAlignment = Alignment.Center) {
                                        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                            Box(Modifier.size(7.dp).background(accent, CircleShape))
                                            Box(Modifier.size(7.dp).background(accent, CircleShape))
                                        }
                                    }
                                    ExpressiveWheelColumn(60, 0, minState, itemH, 90.dp, accent, wheelBg, { toPersianDigits(String.format("%02d", it)) }) { selectedMinute = it }
                                }
                            }
                        }
                    }
                }

                Spacer(Modifier.height(10.dp))

                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.fillMaxWidth()) {
                    reasons.forEach { r ->
                        FilterChip(selected = note == r, onClick = { note = if (note == r) "" else r }, label = { Text(r, style = MaterialTheme.typography.labelSmall) })
                    }
                }

                Spacer(Modifier.height(4.dp))
                OutlinedTextField(value = note, onValueChange = { note = it }, label = { Text("علت یا توضیح (اختیاری)") }, singleLine = true, shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth())

                Spacer(Modifier.height(14.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(0.85f)) { Text("لغو") }
                    Button(
                        onClick = {
                            val outVal = if (isLate) selectedLateMin.toString() else formattedClock
                            onConfirm(outVal, note)
                            onDismiss()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = onAccent),
                        modifier = Modifier.weight(1.45f)
                    ) {
                        Text(
                            text = if (isLate) "ثبت ${toPersianDigits(selectedLateMin.toString())} دقیقه تأخیر" else "ثبت خروج ${toPersianDigits(formattedClock)}",
                            fontWeight = FontWeight.ExtraBold
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ExpressiveWheelColumn(
    count: Int, startFrom: Int, listState: LazyListState, itemH: Dp, wheelWidth: Dp,
    accent: Color, fadeBg: Color, formatValue: (Int) -> String, onValueChange: (Int) -> Unit
) {
    val halfPx = with(LocalDensity.current) { (itemH / 2).roundToPx() }
    val fling = rememberSnapFlingBehavior(lazyListState = listState)
    val haptic = LocalHapticFeedback.current

    val currentIdx by remember {
        derivedStateOf {
            val boost = if (listState.firstVisibleItemScrollOffset >= halfPx) 1 else 0
            (listState.firstVisibleItemIndex + boost).coerceIn(0, count - 1)
        }
    }

    LaunchedEffect(currentIdx) {
        onValueChange(startFrom + currentIdx)
        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
    }

    Box(modifier = Modifier.width(wheelWidth).height(itemH * 3), contentAlignment = Alignment.Center) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = accent.copy(alpha = 0.16f),
            border = BorderStroke(1.8.dp, accent),
            modifier = Modifier.fillMaxWidth().height(itemH)
        ) {}

        LazyColumn(state = listState, flingBehavior = fling, modifier = Modifier.fillMaxWidth().height(itemH * 3)) {
            item { Spacer(Modifier.height(itemH)) }
            items(count) { idx ->
                val isCenter = idx == currentIdx
                val sc by animateFloatAsState(if (isCenter) 1.08f else 0.80f, spring(Spring.DampingRatioMediumBouncy), label = "wSc")
                val al by animateFloatAsState(if (isCenter) 1f else 0.34f, label = "wAl")
                Box(modifier = Modifier.fillMaxWidth().height(itemH).graphicsLayer { scaleX = sc; scaleY = sc; alpha = al }, contentAlignment = Alignment.Center) {
                    Text(
                        text = formatValue(startFrom + idx),
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = if (isCenter) FontWeight.ExtraBold else FontWeight.Medium,
                        color = if (isCenter) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1
                    )
                }
            }
            item { Spacer(Modifier.height(itemH)) }
        }

        Box(modifier = Modifier.align(Alignment.TopCenter).fillMaxWidth().height(36.dp).background(Brush.verticalGradient(listOf(fadeBg, Color.Transparent))))
        Box(modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().height(36.dp).background(Brush.verticalGradient(listOf(Color.Transparent, fadeBg))))
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/StudentAttendanceCard.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Call
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Delete
import androidx.compose.material.icons.rounded.DirectionsRun
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.Grade
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.VerifiedUser
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.PlatformTextStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.LineHeightStyle
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.ui.theme.VazirmatnFontFamily
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.StudentAttendanceRow

@Suppress("DEPRECATION")
private val PeriodDotTextStyle = TextStyle(
    fontFamily = VazirmatnFontFamily,
    fontSize = 10.sp,
    lineHeight = 10.sp,
    fontWeight = FontWeight.ExtraBold,
    platformStyle = PlatformTextStyle(includeFontPadding = false),
    lineHeightStyle = LineHeightStyle(alignment = LineHeightStyle.Alignment.Center, trim = LineHeightStyle.Trim.Both)
)

@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    selectedPeriod: Period,
    onStatusChange: (AttendanceStatus) -> Unit,
    onRequestTimedStatus: (AttendanceStatus) -> Unit,
    onSendIndividualNotice: (StudentAttendanceRow, AttendanceStatus) -> Unit,
    onCallParent: (String) -> Unit,
    onQuickGrade: (StudentAttendanceRow) -> Unit,
    onEditStudent: (StudentAttendanceRow) -> Unit,
    onDeleteStudent: (StudentAttendanceRow) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val accentColor by animateColorAsState(statusPrimaryColor(student.currentStatus), spring(stiffness = Spring.StiffnessMediumLow), label = "acc")
    val activeIdx = when (selectedPeriod) { Period.FIRST -> 0; Period.SECOND -> 1; Period.THIRD -> 2; Period.FOURTH -> 3 }

    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.2.dp, accentColor.copy(alpha = 0.45f)),
        shadowElevation = 2.dp,
        tonalElevation = 2.dp
    ) {
        Column(modifier = Modifier.padding(13.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Surface(shape = CircleShape, color = accentColor.copy(alpha = 0.14f), border = BorderStroke(2.dp, accentColor), modifier = Modifier.size(36.dp)) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(toPersianDigits(indexInClass.toString()), style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.ExtraBold, color = accentColor)
                    }
                }
                Spacer(Modifier.width(9.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text("${student.firstName} ${student.lastName}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = MaterialTheme.colorScheme.onSurface, maxLines = 2, overflow = TextOverflow.Ellipsis)
                    val meta = buildString {
                        if (student.fatherName.isNotBlank()) append("فرزند ${student.fatherName}")
                        if (student.latestGrade.isNotBlank()) { if (isNotEmpty()) append(" • "); append("آخرین نمره: ${toPersianDigits(student.latestGrade)}") }
                    }
                    if (meta.isNotBlank()) Text(meta, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }

                Spacer(Modifier.width(6.dp))

                Row(horizontalArrangement = Arrangement.spacedBy(3.dp), verticalAlignment = Alignment.CenterVertically) {
                    for (i in 0..3) {
                        val raw = student.periodStatuses.getOrElse(i) { AttendanceStatus.UNMARKED }
                        val eff = if (raw == AttendanceStatus.UNMARKED) AttendanceStatus.PRESENT else raw
                        val isAct = i == activeIdx
                        val dotBg by animateColorAsState(statusPrimaryColor(eff), spring(stiffness = Spring.StiffnessMedium), label = "db$i")
                        val dotFg by animateColorAsState(statusOnColor(eff), spring(stiffness = Spring.StiffnessMedium), label = "df$i")
                        Surface(
                            shape = CircleShape,
                            color = dotBg,
                            border = if (isAct) BorderStroke(1.8.dp, Color.White) else null,
                            shadowElevation = if (isAct) 2.dp else 0.dp,
                            modifier = Modifier.size(21.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center, modifier = Modifier.fillMaxSize()) {
                                Text(text = toPersianDigits((i + 1).toString()), style = PeriodDotTextStyle, color = dotFg)
                            }
                        }
                    }
                }
            }

            val showTimedBanner = student.currentStatus == AttendanceStatus.LEFT_CLASS || (student.currentStatus == AttendanceStatus.LATE && (student.eventTime.isNotBlank() || student.note.isNotBlank()))
            AnimatedVisibility(visible = showTimedBanner) {
                val isLateBanner = student.currentStatus == AttendanceStatus.LATE
                val bColor = if (isLateBanner) StatusColors.Late else StatusColors.LeftClass
                Surface(
                    onClick = { onRequestTimedStatus(student.currentStatus) },
                    shape = RoundedCornerShape(12.dp),
                    color = bColor.copy(alpha = 0.14f),
                    border = BorderStroke(1.dp, bColor.copy(alpha = 0.5f)),
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp)
                ) {
                    Row(modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(if (isLateBanner) Icons.Rounded.Schedule else Icons.Rounded.DirectionsRun, null, tint = bColor, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        val info = buildString {
                            if (isLateBanner) {
                                when {
                                    student.eventTime.isBlank() -> append("تأخیر")
                                    student.eventTime.contains(":") -> append("تأخیر ساعت ${toPersianDigits(student.eventTime)}")
                                    else -> append("تأخیر ${toPersianDigits(student.eventTime)} دقیقه")
                                }
                            } else {
                                append("خروج از کلاس")
                                if (student.eventTime.isNotBlank()) append(" ساعت ${toPersianDigits(student.eventTime)}")
                            }
                            if (student.note.isNotBlank()) append(" (${student.note})")
                        }
                        Text(info, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface, modifier = Modifier.weight(1f))
                        Text("ویرایش", style = MaterialTheme.typography.labelSmall, color = bColor, fontWeight = FontWeight.Bold)
                    }
                }
            }

            Spacer(Modifier.height(10.dp))

            Surface(shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth()) {
                Row(modifier = Modifier.fillMaxWidth().padding(3.dp), horizontalArrangement = Arrangement.spacedBy(3.dp)) {
                    AnimatedStatusPill("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, StatusColors.OnPresent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onStatusChange(AttendanceStatus.PRESENT)
                    }
                    AnimatedStatusPill("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, StatusColors.OnAbsent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onStatusChange(AttendanceStatus.ABSENT)
                    }
                    AnimatedStatusPill("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, StatusColors.OnLate, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onRequestTimedStatus(AttendanceStatus.LATE)
                    }
                    AnimatedStatusPill("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, StatusColors.OnExcused, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove); onStatusChange(AttendanceStatus.EXCUSED)
                    }
                    AnimatedStatusPill("خروج", Icons.Rounded.DirectionsRun, student.currentStatus == AttendanceStatus.LEFT_CLASS, StatusColors.LeftClass, StatusColors.OnLeftClass, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onRequestTimedStatus(AttendanceStatus.LEFT_CLASS)
                    }
                }
            }

            Spacer(Modifier.height(9.dp))

            val canNotify = student.currentStatus in listOf(AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.LEFT_CLASS)
            val notifyLabel = when (student.currentStatus) {
                AttendanceStatus.LATE -> "پیام تأخیر"
                AttendanceStatus.LEFT_CLASS -> "پیام خروج"
                else -> "پیام غیبت"
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                ActionPill(notifyLabel, Icons.Rounded.Sms, canNotify, accentColor, statusOnColor(student.currentStatus), Modifier.weight(1.4f)) {
                    onSendIndividualNotice(student, student.currentStatus)
                }
                ActionPill("نمره", Icons.Rounded.Grade, true, MaterialTheme.colorScheme.tertiaryContainer, MaterialTheme.colorScheme.onTertiaryContainer, Modifier.weight(0.9f)) {
                    onQuickGrade(student)
                }
                IconCircle(Icons.Rounded.Call, "تماس", student.mobile.isNotBlank(), MaterialTheme.colorScheme.secondaryContainer, MaterialTheme.colorScheme.onSecondaryContainer) { onCallParent(student.mobile) }
                IconCircle(Icons.Rounded.Edit, "ویرایش", true, MaterialTheme.colorScheme.surfaceContainerHigh, MaterialTheme.colorScheme.onSurface) { onEditStudent(student) }
                IconCircle(Icons.Rounded.Delete, "حذف", true, MaterialTheme.colorScheme.errorContainer, MaterialTheme.colorScheme.onErrorContainer) { onDeleteStudent(student) }
            }
        }
    }
}

@Composable
private fun AnimatedStatusPill(label: String, icon: ImageVector, selected: Boolean, activeBg: Color, activeFg: Color, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val bg by animateColorAsState(if (selected) activeBg else Color.Transparent, spring(stiffness = Spring.StiffnessMediumLow), label = "sBg")
    val fg by animateColorAsState(if (selected) activeFg else MaterialTheme.colorScheme.onSurfaceVariant, spring(stiffness = Spring.StiffnessMediumLow), label = "sFg")
    val corner by animateDpAsState(if (selected) 20.dp else 10.dp, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "sCr")
    val scale by animateFloatAsState(if (selected) 1.04f else 0.96f, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "sSc")

    Column(
        modifier = modifier.graphicsLayer { scaleX = scale; scaleY = scale }.clip(RoundedCornerShape(corner)).background(bg).clickable(onClick = onClick).padding(vertical = 6.dp, horizontal = 2.dp),
        horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center
    ) {
        Icon(icon, label, tint = fg, modifier = Modifier.size(15.dp))
        Text(label, fontSize = 11.sp, fontWeight = if (selected) FontWeight.ExtraBold else FontWeight.SemiBold, color = fg, maxLines = 1, softWrap = false)
    }
}

@Composable
private fun ActionPill(label: String, icon: ImageVector, enabled: Boolean, bg: Color, fg: Color, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val aBg by animateColorAsState(if (enabled) bg else MaterialTheme.colorScheme.surfaceContainer, label = "aBg")
    val aFg by animateColorAsState(if (enabled) fg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f), label = "aFg")
    Row(
        modifier = modifier.clip(RoundedCornerShape(13.dp)).background(aBg).clickable(enabled = enabled, onClick = onClick).padding(vertical = 7.dp, horizontal = 6.dp),
        horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, label, tint = aFg, modifier = Modifier.size(15.dp)); Spacer(Modifier.width(4.dp))
        Text(label, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.ExtraBold, color = aFg, maxLines = 1)
    }
}

@Composable
private fun IconCircle(icon: ImageVector, desc: String, enabled: Boolean, bg: Color, fg: Color, onClick: () -> Unit) {
    Surface(onClick = onClick, enabled = enabled, shape = CircleShape, color = if (enabled) bg else MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.size(33.dp)) {
        Box(contentAlignment = Alignment.Center) {
            Icon(icon, desc, tint = if (enabled) fg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f), modifier = Modifier.size(16.dp))
        }
    }
}

fun statusPrimaryColor(st: AttendanceStatus): Color = when (st) {
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    AttendanceStatus.LEFT_CLASS -> StatusColors.LeftClass
    else -> StatusColors.Present
}

fun statusOnColor(st: AttendanceStatus): Color = when (st) {
    AttendanceStatus.ABSENT -> StatusColors.OnAbsent
    AttendanceStatus.LATE -> StatusColors.OnLate
    AttendanceStatus.EXCUSED -> StatusColors.OnExcused
    AttendanceStatus.LEFT_CLASS -> StatusColors.OnLeftClass
    else -> StatusColors.OnPresent
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) { for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c) }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/JalaliDatePickerDialog.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.JalaliDayCell
import uniffi.hozoor_core.JalaliMonthGrid
import java.time.LocalDate

private val WEEK_HDR = listOf("ش", "ی", "د", "س", "چ", "پ", "ج")

@Composable
fun JalaliDatePickerDialog(initialYear: Int, initialMonth: Int, selectedIso: String, gridProvider: (Int, Int) -> JalaliMonthGrid, onSelectIso: (String) -> Unit, onDismiss: () -> Unit) {
    var year by remember { mutableIntStateOf(initialYear) }
    var month by remember { mutableIntStateOf(initialMonth) }
    val todayIso = remember { LocalDate.now().toString() }
    val grid = remember(year, month) { gridProvider(year, month) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(26.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, tonalElevation = 6.dp) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                    IconButton(onClick = { if (month == 1) { month = 12; year -= 1 } else month -= 1 }) { Icon(Icons.Rounded.ChevronRight, "ماه قبل") }
                    Text(grid.monthLabel, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                    IconButton(onClick = { if (month == 12) { month = 1; year += 1 } else month += 1 }) { Icon(Icons.Rounded.ChevronLeft, "ماه بعد") }
                }
                Spacer(Modifier.height(8.dp))
                Row(modifier = Modifier.fillMaxWidth()) {
                    WEEK_HDR.forEachIndexed { idx, w -> Text(w, modifier = Modifier.weight(1f), textAlign = TextAlign.Center, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.ExtraBold, color = if (idx == 6) StatusColors.Absent else MaterialTheme.colorScheme.primary) }
                }
                Spacer(Modifier.height(6.dp))
                val cells: List<JalaliDayCell?> = List(grid.leadingBlanks) { null } + grid.days
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    cells.chunked(7).forEach { week ->
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            week.forEach { cell ->
                                if (cell == null) Spacer(Modifier.weight(1f).aspectRatio(1f))
                                else {
                                    val isSel = cell.dateIso == selectedIso
                                    val isToday = cell.dateIso == todayIso
                                    Surface(
                                        shape = RoundedCornerShape(10.dp),
                                        color = when { isSel -> MaterialTheme.colorScheme.primary; cell.isFriday -> StatusColors.Absent.copy(alpha = 0.14f); else -> MaterialTheme.colorScheme.surface },
                                        border = if (isToday && !isSel) BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null,
                                        modifier = Modifier.weight(1f).aspectRatio(1f).clip(RoundedCornerShape(10.dp)).clickable { onSelectIso(cell.dateIso); onDismiss() }
                                    ) { Box(contentAlignment = Alignment.Center) { Text(toPersianDigits(cell.day.toString()), style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = when { isSel -> MaterialTheme.colorScheme.onPrimary; cell.isFriday -> StatusColors.Absent; else -> MaterialTheme.colorScheme.onSurface }) } }
                                }
                            }
                            repeat(7 - week.size) { Spacer(Modifier.weight(1f).aspectRatio(1f)) }
                        }
                    }
                }
                Spacer(Modifier.height(14.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("انصراف") }
                    Button(onClick = { onSelectIso(todayIso); onDismiss() }, modifier = Modifier.weight(1f)) { Text("امروز") }
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/StudentEditDialog.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import uniffi.hozoor_core.GradeCategory
import uniffi.hozoor_core.StudentAttendanceRow

@Composable
fun StudentEditDialog(editingStudent: StudentAttendanceRow?, onSave: (String, String, String, String, String) -> Unit, onDismiss: () -> Unit) {
    var first by remember { mutableStateOf(editingStudent?.firstName.orEmpty()) }
    var last by remember { mutableStateOf(editingStudent?.lastName.orEmpty()) }
    var father by remember { mutableStateOf(editingStudent?.fatherName.orEmpty()) }
    var nid by remember { mutableStateOf(editingStudent?.nationalId.orEmpty()) }
    var mobile by remember { mutableStateOf(editingStudent?.mobile.orEmpty()) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
            Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(if (editingStudent == null) "افزودن دانش‌آموز جدید" else "ویرایش دانش‌آموز", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                OutlinedTextField(value = first, onValueChange = { first = it }, label = { Text("نام") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = last, onValueChange = { last = it }, label = { Text("نام خانوادگی") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = father, onValueChange = { father = it }, label = { Text("نام پدر") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = nid, onValueChange = { nid = it.take(10) }, label = { Text("کد ملی (۱۰ رقم)") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = mobile, onValueChange = { mobile = it }, label = { Text("شماره موبایل") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("لغو") }
                    Button(onClick = { onSave(first, last, father, nid, mobile); onDismiss() }, modifier = Modifier.weight(1f)) { Text("ذخیره") }
                }
            }
        }
    }
}

@Composable
fun QuickGradeDialog(studentName: String, categories: List<GradeCategory>, initialCategoryId: Long, initialScore: String, initialNote: String, onSave: (Long, String, String) -> Unit, onDismiss: () -> Unit) {
    var catId by remember { mutableLongStateOf(initialCategoryId.takeIf { it > 0 } ?: categories.firstOrNull()?.id ?: 0L) }
    var score by remember { mutableStateOf(initialScore) }
    var note by remember { mutableStateOf(initialNote) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
            Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("ثبت نمره", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                Text(studentName, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary)
                if (categories.isNotEmpty()) {
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(categories, key = { it.id }) { cat -> FilterChip(selected = cat.id == catId, onClick = { catId = cat.id }, label = { Text(cat.name) }) }
                    }
                }
                OutlinedTextField(value = score, onValueChange = { score = it }, label = { Text("نمره (مثلاً ۱۹.۵ یا شایسته)") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = note, onValueChange = { note = it }, label = { Text("توضیح اختیاری") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("انصراف") }
                    Button(onClick = { if (catId > 0) onSave(catId, score, note); onDismiss() }, modifier = Modifier.weight(1f)) { Text("ذخیره نمره") }
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExpressiveToolbar.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.DoneAll
import androidx.compose.material.icons.rounded.PersonAdd
import androidx.compose.material.icons.rounded.Share
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FloatingToolbarDefaults
import androidx.compose.material3.HorizontalFloatingToolbar
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import uniffi.hozoor_core.Period

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun ExpressiveAttendanceToolbar(
    selectedPeriod: Period, onResetAllPresent: () -> Unit, onCopyFromPrevious: () -> Unit,
    onAddStudent: () -> Unit, onOpenExportSheet: () -> Unit, onImportFile: () -> Unit, modifier: Modifier = Modifier
) {
    HorizontalFloatingToolbar(
        expanded = true, modifier = modifier,
        colors = FloatingToolbarDefaults.vibrantFloatingToolbarColors(),
        floatingActionButton = { FloatingToolbarDefaults.VibrantFloatingActionButton(onClick = onImportFile) { Icon(Icons.Rounded.UploadFile, "ورود اکسل یا CSV") } }
    ) {
        IconButton(onClick = onResetAllPresent) { Icon(Icons.Rounded.DoneAll, "همه حاضر") }
        IconButton(onClick = onCopyFromPrevious, enabled = selectedPeriod != Period.FIRST) { Icon(Icons.Rounded.ContentCopy, "کپی زنگ قبل") }
        IconButton(onClick = onAddStudent) { Icon(Icons.Rounded.PersonAdd, "افزودن دانش‌آموز") }
        IconButton(onClick = onOpenExportSheet) { Icon(Icons.Rounded.Share, "مرکز ارسال، مخاطبین و پشتیبان") }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExportAndReportSheet.kt": r'''package ir.hozoor.app.ui.components

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
                                val sub = when {
                                    st.currentStatus == AttendanceStatus.LEFT_CLASS && st.eventTime.isNotBlank() -> "خروج ساعت ${toPersianDigits(st.eventTime)}"
                                    st.currentStatus == AttendanceStatus.LATE && st.eventTime.contains(":") -> "تأخیر ساعت ${toPersianDigits(st.eventTime)}"
                                    st.currentStatus == AttendanceStatus.LATE && st.eventTime.isNotBlank() -> "تأخیر ${toPersianDigits(st.eventTime)} دقیقه"
                                    else -> statusLabelFa(st.currentStatus)
                                }
                                Text(sub, style = MaterialTheme.typography.labelSmall, color = statusPrimaryColor(st.currentStatus))
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
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/GradebookScreen.kt": r'''package ir.hozoor.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
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
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Delete
import androidx.compose.material.icons.rounded.Search
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
import ir.hozoor.app.util.FileShareHelper
import uniffi.hozoor_core.GradeCategory
import uniffi.hozoor_core.StudentGradeRow

@Composable
fun GradebookContent(
    majors: List<String>, selectedMajor: String,
    grades: List<String>, selectedGrade: String,
    sections: List<Int>, selectedSection: Int,
    onSelectMajor: (String) -> Unit, onSelectGrade: (String) -> Unit, onSelectSection: (Int) -> Unit,
    categories: List<GradeCategory>,
    selectedCategoryId: Long,
    studentGrades: List<StudentGradeRow>,
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    onSelectCategory: (Long) -> Unit,
    onAddCategory: (String) -> Unit,
    onDeleteCategory: (Long) -> Unit,
    onSaveGrade: (Long, Long, String, String) -> Unit,
    onExportGradebookExcel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var showAddCatDialog by remember { mutableStateOf(false) }
    var editingRow by remember { mutableStateOf<StudentGradeRow?>(null) }

    val filtered = remember(studentGrades, searchQuery) {
        val q = FileShareHelper.normalizePersianSearch(searchQuery)
        if (q.isEmpty()) studentGrades
        else studentGrades.filter { r ->
            FileShareHelper.normalizePersianSearch("${r.firstName} ${r.lastName} ${r.fatherName} ${r.score}").contains(q)
        }
    }

    LazyColumn(modifier = modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 32.dp, top = 2.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
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
                            FilterChip(selected = cat.id == selectedCategoryId, onClick = { onSelectCategory(cat.id) }, label = { Text(cat.name, fontWeight = if (cat.id == selectedCategoryId) FontWeight.ExtraBold else FontWeight.Medium) })
                        }
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        OutlinedButton(onClick = onExportGradebookExcel, modifier = Modifier.weight(1f)) {
                            Icon(Icons.Rounded.TableChart, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(5.dp)); Text("خروجی اکسل دفتر نمره")
                        }
                        if (categories.size > 1 && selectedCategoryId > 0) {
                            IconButton(onClick = { onDeleteCategory(selectedCategoryId) }) { Icon(Icons.Rounded.Delete, "حذف عنوان", tint = MaterialTheme.colorScheme.error) }
                        }
                    }
                }
            }
        }
        item(key = "gb_search") {
            OutlinedTextField(
                value = searchQuery, onValueChange = onSearchChange,
                placeholder = { Text("جستجوی دانش‌آموز در دفتر نمره...") },
                leadingIcon = { Icon(Icons.Rounded.Search, null) },
                trailingIcon = { if (searchQuery.isNotEmpty()) IconButton(onClick = { onSearchChange("") }) { Icon(Icons.Rounded.Close, "پاک کردن") } },
                singleLine = true, shape = RoundedCornerShape(22.dp), modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
            )
        }
        itemsIndexed(filtered, key = { _, r -> r.studentId }) { idx, row ->
            Surface(onClick = { editingRow = row }, shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainerLow, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
                Row(modifier = Modifier.padding(13.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("${toPersianDigits((idx + 1).toString())}. ${row.firstName} ${row.lastName}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        val sub = buildString {
                            if (row.fatherName.isNotBlank()) append("فرزند ${row.fatherName}")
                            if (row.note.isNotBlank()) { if (isNotEmpty()) append(" • "); append(row.note) }
                        }
                        if (sub.isNotBlank()) Text(sub, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Surface(shape = RoundedCornerShape(14.dp), color = if (row.score.isNotBlank()) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainerHigh) {
                        Text(
                            text = if (row.score.isNotBlank()) toPersianDigits(row.score) else "ثبت نمره",
                            style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.ExtraBold,
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
        QuickGradeDialog("${row.firstName} ${row.lastName}", categories, selectedCategoryId, row.score, row.note, { cid, sc, nt -> onSaveGrade(row.studentId, cid, sc, nt) }) { editingRow = null }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/MonthlyReportScreen.kt": r'''package ir.hozoor.app.ui.screens

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

        item(key = "m_search") {
            OutlinedTextField(
                value = searchQuery, onValueChange = onSearchChange,
                placeholder = { Text("جستجوی دانش‌آموز در گزارش ماهانه...") },
                leadingIcon = { Icon(Icons.Rounded.Search, null) },
                trailingIcon = { if (searchQuery.isNotEmpty()) IconButton(onClick = { onSearchChange("") }) { Icon(Icons.Rounded.Close, "پاک کردن") } },
                singleLine = true, shape = RoundedCornerShape(22.dp), modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
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

    if (inspectingStudent != null) {
        StudentMonthlyDetailsDialog(inspectingStudent, report?.monthLabel.orEmpty(), inspectingEvents, onDismissInspect)
    }
}

@Composable
private fun StudentMonthlyDetailsDialog(student: MonthlyStudentStat, monthLabel: String, events: List<StudentMonthlyEvent>, onDismiss: () -> Unit) {
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
                                            if (ev.eventTime.isNotBlank()) {
                                                if (ev.status == AttendanceStatus.LATE && !ev.eventTime.contains(":")) {
                                                    append(" • ${toPersianDigits(ev.eventTime)} دقیقه")
                                                } else {
                                                    append(" • ساعت ${toPersianDigits(ev.eventTime)}")
                                                }
                                            }
                                            if (ev.note.isNotBlank()) append(" • ${ev.note}")
                                        }
                                        Text(detail, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    }
                                    Surface(shape = RoundedCornerShape(12.dp), color = stColor) {
                                        Text(statusLabelFa(ev.status), style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.ExtraBold, color = statusOnColor(ev.status), modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp))
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
                Text("غیبت موجه:${toPersianDigits(stat.excusedPeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.Excused)
                Text("خروج:${toPersianDigits(stat.leftClassPeriods.toString())}", style = MaterialTheme.typography.labelSmall, color = StatusColors.LeftClass)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/AttendanceScreen.kt": r'''package ir.hozoor.app.ui.screens

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.ContactsContract
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
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
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CalendarMonth
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.DarkMode
import androidx.compose.material.icons.rounded.ExpandLess
import androidx.compose.material.icons.rounded.ExpandMore
import androidx.compose.material.icons.rounded.LightMode
import androidx.compose.material.icons.rounded.Palette
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LoadingIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ir.hozoor.app.ui.components.ClassCategorySelector
import ir.hozoor.app.ui.components.ExportAndReportSheet
import ir.hozoor.app.ui.components.ExpressiveAttendanceToolbar
import ir.hozoor.app.ui.components.JalaliDatePickerDialog
import ir.hozoor.app.ui.components.PeriodSelector
import ir.hozoor.app.ui.components.QuickGradeDialog
import ir.hozoor.app.ui.components.StudentAttendanceCard
import ir.hozoor.app.ui.components.StudentEditDialog
import ir.hozoor.app.ui.components.TimeWheelDialog
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.state.AttendanceViewModel
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.util.FileShareHelper
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.StudentAttendanceRow

private val IMPORT_MIMES = arrayOf(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel", "text/csv", "text/comma-separated-values", "application/csv", "text/plain"
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class, ExperimentalMaterial3Api::class)
@Composable
fun AttendanceScreen(viewModel: AttendanceViewModel, isDarkTheme: Boolean) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val snackbar = remember { SnackbarHostState() }

    var showExportSheet by remember { mutableStateOf(false) }
    var showDatePicker by remember { mutableStateOf(false) }
    var showTeacherPanel by remember { mutableStateOf(false) }
    var showAddDialog by remember { mutableStateOf(false) }
    var editingStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var timedStatusTarget by remember { mutableStateOf<Pair<StudentAttendanceRow, AttendanceStatus>?>(null) }
    var gradingStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var deletingStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var showDeleteClassDialog by remember { mutableStateOf(false) }
    var pendingBackupBytes by remember { mutableStateOf<ByteArray?>(null) }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        val name = FileShareHelper.resolveFileName(context, uri)
        context.contentResolver.openInputStream(uri)?.use { s -> viewModel.importFileBytes(name, s.readBytes(), true) }
    }

    val contactPicker = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { res ->
        val uri = res.data?.data ?: return@rememberLauncherForActivityResult
        val picked = FileShareHelper.extractPhoneContact(context, uri)
        if (picked != null) viewModel.saveContact(picked.first, "مخاطب", picked.second)
        else viewModel.setSheetFeedback("شماره معتبری برای این مخاطب پیدا نشد")
    }

    val saveBackupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        val b = pendingBackupBytes; pendingBackupBytes = null
        if (uri != null && b != null) {
            runCatching { context.contentResolver.openOutputStream(uri)?.use { it.write(b) }; viewModel.showMessage("پشتیبان کامل در گوشی ذخیره شد") }
                .onFailure { viewModel.showMessage("خطا در ذخیره فایل") }
        }
    }

    val restorePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        context.contentResolver.openInputStream(uri)?.use { s -> viewModel.restoreBackupJson(s.bufferedReader(Charsets.UTF_8).readText()) }
    }

    fun buildStudentNotice(s: StudentAttendanceRow, st: AttendanceStatus): String {
        val nPart = if (s.note.isNotBlank()) " (${s.note})" else ""
        val statusText = when (st) {
            AttendanceStatus.LATE -> {
                val tStr = when {
                    s.eventTime.isBlank() -> "با تأخیر"
                    s.eventTime.contains(":") -> "با تأخیر (ساعت ${toPersianDigits(s.eventTime)})"
                    else -> "با ${toPersianDigits(s.eventTime)} دقیقه تأخیر"
                }
                "$tStr$nPart حاضر شده است"
            }
            AttendanceStatus.LEFT_CLASS -> {
                val tStr = if (s.eventTime.isNotBlank()) " ساعت ${toPersianDigits(s.eventTime)}" else ""
                "از کلاس خارج شده$tStr$nPart"
            }
            AttendanceStatus.EXCUSED -> "دارای غیبت موجه بوده است"
            else -> "غایب بوده است"
        }
        val pTitle = when (state.selectedPeriod) { Period.FIRST -> "زنگ اول"; Period.SECOND -> "زنگ دوم"; Period.THIRD -> "زنگ سوم"; Period.FOURTH -> "زنگ چهارم" }
        val cls = buildString {
            if (state.selectedMajor.isNotBlank()) append("${state.selectedMajor} - ")
            append("پایه ${state.selectedGrade}")
            if (state.sectionsForSelection.size > 1) append(" شعبه ${toPersianDigits(state.selectedSection.toString())}")
        }
        val les = if (state.lessonName.isNotBlank()) "در درس ${state.lessonName} " else ""
        val tch = if (state.teacherName.isNotBlank()) " با دبیر ${state.teacherName}" else ""
        return "سلام علیکم، دانش‌آموز ${s.firstName} ${s.lastName}، فرزند ${s.fatherName.ifBlank { "ثبت نشده" }}، $cls، ${les}مورخه ${state.jalaliDate} ($pTitle)$tch $statusText."
    }

    LaunchedEffect(state.snackbarMessage) {
        state.snackbarMessage?.let { snackbar.showSnackbar(it); viewModel.clearSnackbar() }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbar) }, containerColor = MaterialTheme.colorScheme.background) { pad ->
        Box(modifier = Modifier.fillMaxSize().padding(pad)) {
            Column(modifier = Modifier.fillMaxSize()) {
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(state.selectedClass?.schoolName?.ifBlank { "سامانه حضور و غیاب" } ?: "سامانه حضور و غیاب", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold)
                        Text(state.jalaliDate, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        FilledTonalIconButton(onClick = viewModel::toggleDynamicColor) {
                            Icon(Icons.Rounded.Palette, "رنگ پویا", tint = if (state.dynamicColorEnabled) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Spacer(Modifier.width(4.dp))
                    }
                    FilledTonalIconButton(onClick = { viewModel.toggleDarkMode(isDarkTheme) }) {
                        Icon(if (isDarkTheme) Icons.Rounded.LightMode else Icons.Rounded.DarkMode, "تم")
                    }
                }

                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    FilledTonalButton(onClick = { showDatePicker = true }, contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp), modifier = Modifier.weight(1f)) {
                        Icon(Icons.Rounded.CalendarMonth, null, modifier = Modifier.size(17.dp)); Spacer(Modifier.width(5.dp)); Text("تقویم شمسی", maxLines = 1)
                    }
                    IconButton(onClick = { viewModel.shiftDate(-1) }) { Icon(Icons.Rounded.ChevronRight, "روز قبل") }
                    IconButton(onClick = { viewModel.shiftDate(1) }) { Icon(Icons.Rounded.ChevronLeft, "روز بعد") }
                    OutlinedButton(onClick = { showTeacherPanel = !showTeacherPanel }, contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)) {
                        Text("دبیر و درس"); Icon(if (showTeacherPanel) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null)
                    }
                }

                AnimatedVisibility(visible = showTeacherPanel) {
                    Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp), shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainerLow) {
                        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(value = state.teacherName, onValueChange = viewModel::updateTeacherName, label = { Text("نام دبیر") }, singleLine = true, modifier = Modifier.weight(1f))
                                OutlinedTextField(value = state.lessonName, onValueChange = viewModel::updateLessonName, label = { Text("نام درس") }, singleLine = true, modifier = Modifier.weight(1f))
                            }
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(value = state.principalPhone, onValueChange = viewModel::updatePrincipalPhone, label = { Text("موبایل مدیر") }, singleLine = true, modifier = Modifier.weight(1.4f))
                                OutlinedTextField(value = state.classTime, onValueChange = viewModel::updateClassTime, label = { Text("ساعت") }, singleLine = true, modifier = Modifier.weight(0.8f))
                            }
                        }
                    }
                }

                if (state.classes.isNotEmpty()) {
                    Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        FilterChip(selected = state.activeTab == 0, onClick = { viewModel.switchTab(0) }, label = { Text("حضور روزانه", maxLines = 1) }, modifier = Modifier.weight(1f))
                        FilterChip(selected = state.activeTab == 1, onClick = { viewModel.switchTab(1) }, label = { Text("دفتر نمره", maxLines = 1) }, modifier = Modifier.weight(1f))
                        FilterChip(selected = state.activeTab == 2, onClick = { viewModel.switchTab(2) }, label = { Text("آمار و ماهانه", maxLines = 1) }, modifier = Modifier.weight(1f))
                    }
                }

                when {
                    state.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { LoadingIndicator() }
                    state.classes.isEmpty() -> EmptyImportState(
                        onImportClick = { filePicker.launch(IMPORT_MIMES) },
                        onLoadSampleClick = { runCatching { context.assets.open("sample_school.csv").use { s -> viewModel.importFileBytes("sample_school.csv", s.readBytes(), true) } } },
                        onDownloadTemplate = { viewModel.exportTemplateExcel { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b, "نمونه Excel") } },
                        onRestoreBackup = { restorePicker.launch(arrayOf("application/json", "text/plain", "*/*")) }
                    )
                    else -> {
                        AnimatedContent(state.activeTab, transitionSpec = { fadeIn(tween(200)) togetherWith fadeOut(tween(150)) }, label = "tabs") { tab ->
                            when (tab) {
                                1 -> GradebookContent(
                                    majors = state.majors, selectedMajor = state.selectedMajor,
                                    grades = state.gradesForSelection, selectedGrade = state.selectedGrade,
                                    sections = state.sectionsForSelection, selectedSection = state.selectedSection,
                                    onSelectMajor = viewModel::selectMajor, onSelectGrade = viewModel::selectGrade, onSelectSection = viewModel::selectSection,
                                    categories = state.gradeCategories, selectedCategoryId = state.selectedGradeCategoryId,
                                    studentGrades = state.classGrades,
                                    searchQuery = state.gradebookSearchQuery, onSearchChange = viewModel::updateGradebookSearch,
                                    onSelectCategory = viewModel::selectGradeCategory, onAddCategory = viewModel::addGradeCategory,
                                    onDeleteCategory = viewModel::deleteGradeCategory, onSaveGrade = viewModel::setStudentGrade,
                                    onExportGradebookExcel = { viewModel.exportGradebookExcel { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b, "اکسل دفتر نمره") } }
                                )
                                2 -> MonthlyReportContent(
                                    majors = state.majors, selectedMajor = state.selectedMajor,
                                    grades = state.gradesForSelection, selectedGrade = state.selectedGrade,
                                    sections = state.sectionsForSelection, selectedSection = state.selectedSection,
                                    onSelectMajor = viewModel::selectMajor, onSelectGrade = viewModel::selectGrade, onSelectSection = viewModel::selectSection,
                                    analytics = state.classAnalytics, report = state.monthlyReport,
                                    searchQuery = state.monthlySearchQuery, onSearchChange = viewModel::updateMonthlySearch,
                                    sortByAbsence = state.sortMonthlyByAbsence,
                                    onShiftMonth = viewModel::shiftJalaliMonth, onToggleSort = viewModel::toggleMonthlySort,
                                    onInspectStudent = viewModel::openStudentMonthlyDetails,
                                    inspectingStudent = state.inspectingMonthlyStudent,
                                    inspectingEvents = state.inspectingMonthlyEvents,
                                    onDismissInspect = viewModel::closeStudentMonthlyDetails,
                                    onExportExcel = { viewModel.exportMonthlyExcel { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b, "اکسل ماهانه") } },
                                    onExportCsv = { viewModel.exportMonthlyCsv { n, b -> FileShareHelper.shareBytesAsFile(context, n, "text/csv", b, "CSV ماهانه") } },
                                    onRequestDeleteClass = { showDeleteClassDialog = true }
                                )
                                else -> LazyColumn(modifier = Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 104.dp, top = 2.dp)) {
                                    item(key = "cat_grid") {
                                        ClassCategorySelector(state.majors, state.selectedMajor, state.gradesForSelection, state.selectedGrade, state.sectionsForSelection, state.selectedSection, viewModel::selectMajor, viewModel::selectGrade, viewModel::selectSection)
                                    }
                                    item(key = "p_bar") {
                                        Spacer(Modifier.height(6.dp))
                                        PeriodSelector(state.selectedPeriod, viewModel::selectPeriod)
                                        SummaryHeaderCard(state.summary)
                                        OutlinedTextField(
                                            value = state.searchQuery, onValueChange = viewModel::updateSearch,
                                            placeholder = { Text("جستجوی نام، نام خانوادگی، پدر یا کد ملی...") },
                                            leadingIcon = { Icon(Icons.Rounded.Search, null) },
                                            trailingIcon = { if (state.searchQuery.isNotEmpty()) IconButton(onClick = { viewModel.updateSearch("") }) { Icon(Icons.Rounded.Close, "پاک") } },
                                            singleLine = true, shape = RoundedCornerShape(22.dp),
                                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                                        )
                                    }
                                    itemsIndexed(state.students, key = { _, s -> s.studentId }, contentType = { _, _ -> "stu" }) { idx, stu ->
                                        StudentAttendanceCard(
                                            indexInClass = idx + 1, student = stu, selectedPeriod = state.selectedPeriod,
                                            onStatusChange = { viewModel.setStudentStatus(stu.studentId, it) },
                                            onRequestTimedStatus = { st -> timedStatusTarget = stu to st },
                                            onSendIndividualNotice = { s, st ->
                                                val phone = state.principalPhone.ifBlank { s.mobile }
                                                FileShareHelper.openSmsApp(context, phone, buildStudentNotice(s, st))
                                            },
                                            onCallParent = { ph -> context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$ph"))) },
                                            onQuickGrade = { gradingStudent = it },
                                            onEditStudent = { editingStudent = it },
                                            onDeleteStudent = { deletingStudent = it }
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (state.activeTab == 0 && state.classes.isNotEmpty()) {
                ExpressiveAttendanceToolbar(
                    selectedPeriod = state.selectedPeriod,
                    onResetAllPresent = viewModel::resetAllToPresent,
                    onCopyFromPrevious = viewModel::copyFromPreviousPeriod,
                    onAddStudent = { showAddDialog = true },
                    onOpenExportSheet = { viewModel.prepareExportSheet(false); showExportSheet = true },
                    onImportFile = { filePicker.launch(IMPORT_MIMES) },
                    modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp)
                )
            }
        }
    }

    if (showDatePicker) {
        val ym = remember(state.selectedDate) { viewModel.currentDateJalaliYearMonth() }
        JalaliDatePickerDialog(ym.year, ym.month, state.selectedDate.toString(), viewModel::getJalaliCalendarGrid, viewModel::selectDateIso) { showDatePicker = false }
    }
    timedStatusTarget?.let { (stu, targetStatus) ->
        TimeWheelDialog(
            student = stu,
            targetStatus = targetStatus,
            onConfirm = { value, reason -> viewModel.setStudentStatus(stu.studentId, targetStatus, value, reason) },
            onDismiss = { timedStatusTarget = null }
        )
    }
    gradingStudent?.let { stu ->
        QuickGradeDialog("${stu.firstName} ${stu.lastName}", state.gradeCategories, state.selectedGradeCategoryId, stu.latestGrade, "", { cid, sc, nt -> viewModel.setStudentGrade(stu.studentId, cid, sc, nt) }) { gradingStudent = null }
    }
    if (showAddDialog) StudentEditDialog(null, { f, l, fa, nid, mob -> viewModel.addStudentToCurrentClass(f, l, fa, nid, mob) }) { showAddDialog = false }
    editingStudent?.let { st -> StudentEditDialog(st, { f, l, fa, nid, mob -> viewModel.updateStudent(st.studentId, f, l, fa, nid, mob) }) { editingStudent = null } }
    deletingStudent?.let { st ->
        AlertDialog(
            onDismissRequest = { deletingStudent = null }, title = { Text("حذف دانش‌آموز") },
            text = { Text("آیا «${st.firstName} ${st.lastName}» و سوابقش حذف شوند؟") },
            confirmButton = { TextButton(onClick = { viewModel.deleteStudent(st.studentId); deletingStudent = null }) { Text("حذف", color = MaterialTheme.colorScheme.error) } },
            dismissButton = { TextButton(onClick = { deletingStudent = null }) { Text("انصراف") } }
        )
    }
    if (showDeleteClassDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteClassDialog = false }, title = { Text("حذف کامل کلاس") },
            text = { Text("تمام دانش‌آموزان و سوابق این کلاس حذف می‌شوند. ادامه می‌دهید؟") },
            confirmButton = { TextButton(onClick = { viewModel.deleteCurrentClass(); showDeleteClassDialog = false }) { Text("حذف کلاس", color = MaterialTheme.colorScheme.error) } },
            dismissButton = { TextButton(onClick = { showDeleteClassDialog = false }) { Text("انصراف") } }
        )
    }

    if (showExportSheet) {
        ExportAndReportSheet(
            report = state.principalReport,
            summary = state.summary,
            students = state.students,
            savedContacts = state.savedContacts,
            backupStats = state.backupStats,
            wholeSchool = state.reportWholeSchool,
            recipientName = state.recipientName,
            recipientPhone = state.principalPhone,
            feedbackMessage = state.sheetFeedback,
            onToggleWholeSchool = { viewModel.prepareExportSheet(it) },
            onRecipientPhoneChange = viewModel::updatePrincipalPhone,
            onPickPhoneContact = {
                runCatching { contactPicker.launch(FileShareHelper.createPickPhoneContactIntent(context)) }
                    .onFailure {
                        runCatching { contactPicker.launch(Intent(Intent.ACTION_PICK, ContactsContract.CommonDataKinds.Phone.CONTENT_URI)) }
                            .onFailure { viewModel.setSheetFeedback("اپلیکیشن مخاطبین پیدا نشد؛ شماره را دستی وارد کنید.") }
                    }
            },
            onSelectSavedContact = { c -> viewModel.updateRecipient(c.name, c.phone) },
            onSaveCurrentContact = { n, p -> viewModel.saveContact(n, "", p) },
            onDeleteSavedContact = viewModel::deleteContact,
            onLoadPeriodGroupMessage = viewModel::generatePeriodGroupMessage,
            onSendSms = { ph, txt -> if (!FileShareHelper.openSmsApp(context, ph, txt)) viewModel.setSheetFeedback("برنامه پیامک باز نشد") },
            onSendWhatsApp = { ph, txt -> FileShareHelper.openWhatsApp(context, ph, txt) },
            onShareText = { txt -> FileShareHelper.shareText(context, txt, "ارسال گزارش") },
            onCopyText = { txt -> FileShareHelper.copyToClipboard(context, "گزارش", txt); viewModel.showMessage("متن کپی شد"); showExportSheet = false },
            onNotifyParentSms = { st -> FileShareHelper.openSmsApp(context, st.mobile, buildStudentNotice(st, st.currentStatus)) },
            onNotifyParentWhatsApp = { st -> FileShareHelper.openWhatsApp(context, st.mobile, buildStudentNotice(st, st.currentStatus)) },
            onExportDailyExcel = { viewModel.exportDailyExcel(state.reportWholeSchool) { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b, "اکسل حضور") } },
            onExportGradebookExcel = { viewModel.exportGradebookExcel { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b, "اکسل نمرات") } },
            onExportCsv = { viewModel.exportCurrentClassCsv { n, b -> FileShareHelper.shareBytesAsFile(context, n, "text/csv", b, "فایل CSV") } },
            onExportTemplateExcel = { viewModel.exportTemplateExcel { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b, "نمونه Excel") } },
            onSaveBackupToDevice = { viewModel.exportBackupJson { n, b -> pendingBackupBytes = b; saveBackupLauncher.launch(n) } },
            onShareBackupJson = { viewModel.exportBackupJson { n, b -> FileShareHelper.shareBytesAsFile(context, n, "application/json", b, "پشتیبان کامل") } },
            onRestoreBackupJson = { showExportSheet = false; restorePicker.launch(arrayOf("application/json", "text/plain", "*/*")) },
            onDismiss = { showExportSheet = false }
        )
    }
}

@Composable
private fun SummaryHeaderCard(summary: PeriodSummary) {
    Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp), shape = RoundedCornerShape(20.dp), color = MaterialTheme.colorScheme.surfaceContainer) {
        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 9.dp, horizontal = 10.dp), horizontalArrangement = Arrangement.SpaceBetween) {
            MetricPill("حاضر", summary.present, StatusColors.Present)
            MetricPill("غایب", summary.absent, StatusColors.Absent)
            MetricPill("تأخیر", summary.late, StatusColors.Late)
            MetricPill("غیبت موجه", summary.excused, StatusColors.Excused)
            MetricPill("خروج", summary.leftClass, StatusColors.LeftClass)
        }
    }
}

@Composable
private fun MetricPill(label: String, count: Int, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(toPersianDigits(count.toString()), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun EmptyImportState(onImportClick: () -> Unit, onLoadSampleClick: () -> Unit, onDownloadTemplate: () -> Unit, onRestoreBackup: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize().padding(32.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text("سامانه حضور و غیاب آماده است", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold)
        Spacer(Modifier.height(8.dp))
        Text("فایل اکسل (.xlsx) یا CSV را وارد کنید تا کلاس‌ها بر اساس رشته، پایه و شعبه دسته‌بندی شوند.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(20.dp))
        Button(onClick = onImportClick, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Rounded.UploadFile, null); Spacer(Modifier.width(8.dp)); Text("انتخاب فایل اکسل یا CSV") }
        Spacer(Modifier.height(8.dp))
        FilledTonalButton(onClick = onLoadSampleClick, modifier = Modifier.fillMaxWidth()) { Text("تست سریع با داده‌های نمونه") }
        Spacer(Modifier.height(8.dp))
        OutlinedButton(onClick = onDownloadTemplate, modifier = Modifier.fillMaxWidth()) { Text("دریافت فایل نمونه Excel (XLSX)") }
        Spacer(Modifier.height(8.dp))
        OutlinedButton(onClick = onRestoreBackup, modifier = Modifier.fillMaxWidth()) { Text("بازیابی از پشتیبان قبلی (JSON)") }
    }
}
''',
}


def main():
    for stale in STALE_FILES:
        sp = Path(stale)
        if sp.exists():
            sp.unlink()
            print(f"Removed stale: {stale}")
    for rel, content in FILES.items():
        p = Path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
        print(f"Created: {rel}")
    print(f"\nPart 3 (Android Screens v5.1) done: {len(FILES)} files.")


if __name__ == "__main__":
    main()
