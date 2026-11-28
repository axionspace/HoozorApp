package ir.hozoor.app.ui.components

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
