package ir.hozoor.app.ui.components

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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AccessTimeFilled
import androidx.compose.material.icons.rounded.DirectionsRun
import androidx.compose.material.icons.rounded.MyLocation
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
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
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.theme.StatusColors
import kotlinx.coroutines.launch
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.StudentAttendanceRow
import java.time.LocalTime

private val LATE_REASONS = listOf("ترافیک / سرویس", "خواب ماندن", "هماهنگ با دفتر", "تأخیر غیرموجه")
private val EXIT_REASONS = listOf("برنگشت", "با اجازه", "دفتر / معاون", "بهداشت / آبخوری")

/** چرخ اسکرول ساعت استوانه‌ای و مدرن برای هر دو وضعیت «تأخیر» و «خروج از کلاس» با پیش‌فرض ساعت گوشی */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun TimeWheelDialog(
    student: StudentAttendanceRow,
    targetStatus: AttendanceStatus,
    onConfirm: (time: String, reason: String) -> Unit,
    onDismiss: () -> Unit
) {
    val isLate = targetStatus == AttendanceStatus.LATE
    val accent = if (isLate) StatusColors.Late else StatusColors.LeftClass
    val onAccent = if (isLate) StatusColors.OnLate else StatusColors.OnLeftClass
    val title = if (isLate) "ثبت ساعت ورود (تأخیر)" else "ثبت ساعت خروج از کلاس"
    val reasons = if (isLate) LATE_REASONS else EXIT_REASONS
    val defaultReason = if (isLate) "" else "برنگشت"

    val now = remember { LocalTime.now() }
    val initParts = remember(student.eventTime, targetStatus) {
        val useExisting = student.currentStatus == targetStatus && student.eventTime.contains(":")
        val sp = if (useExisting) student.eventTime.split(":") else emptyList()
        val h = sp.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: now.hour
        val m = sp.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: now.minute
        h to m
    }

    val hourState = rememberLazyListState(initialFirstVisibleItemIndex = initParts.first)
    val minState = rememberLazyListState(initialFirstVisibleItemIndex = initParts.second)
    val scope = rememberCoroutineScope()

    var selectedHour by remember { mutableIntStateOf(initParts.first) }
    var selectedMinute by remember { mutableIntStateOf(initParts.second) }
    var note by remember { mutableStateOf(if (student.currentStatus == targetStatus) student.note else defaultReason) }

    val formattedTime = String.format("%02d:%02d", selectedHour, selectedMinute)
    val cardBg = MaterialTheme.colorScheme.surfaceContainerHigh

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(30.dp), color = cardBg, tonalElevation = 8.dp) {
            Column(modifier = Modifier.padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                // هدر زیبا با آیکون دایره‌ای رنگی
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

                Spacer(Modifier.height(10.dp))

                // نمایشگر دیجیتال زنده ساعت انتخاب‌شده
                Surface(shape = RoundedCornerShape(20.dp), color = accent.copy(alpha = 0.14f), border = BorderStroke(1.5.dp, accent.copy(alpha = 0.45f))) {
                    Row(modifier = Modifier.padding(horizontal = 18.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.AccessTimeFilled, null, tint = accent, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text(toPersianDigits(formattedTime), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold, color = MaterialTheme.colorScheme.onSurface)
                    }
                }

                Spacer(Modifier.height(12.dp))

                // چرخ استوانه‌ای مدرن با افکت عمق سه‌بعدی و محو شدن نرم بالا و پایین
                Surface(
                    shape = RoundedCornerShape(24.dp),
                    color = MaterialTheme.colorScheme.surfaceContainerLowest,
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 10.dp, horizontal = 12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.Center
                        ) {
                            ExpressiveWheelColumn(24, hourState, "ساعت", accent, MaterialTheme.colorScheme.surfaceContainerLowest) { selectedHour = it }
                            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(horizontal = 12.dp, vertical = 14.dp)) {
                                Box(Modifier.size(7.dp).background(accent, CircleShape))
                                Spacer(Modifier.height(8.dp))
                                Box(Modifier.size(7.dp).background(accent, CircleShape))
                            }
                            ExpressiveWheelColumn(60, minState, "دقیقه", accent, MaterialTheme.colorScheme.surfaceContainerLowest) { selectedMinute = it }
                        }
                    }
                }

                Spacer(Modifier.height(12.dp))

                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.fillMaxWidth()) {
                    reasons.forEach { r ->
                        FilterChip(selected = note == r, onClick = { note = if (note == r) "" else r }, label = { Text(r, style = MaterialTheme.typography.labelSmall) })
                    }
                }

                Spacer(Modifier.height(4.dp))
                OutlinedTextField(
                    value = note, onValueChange = { note = it },
                    label = { Text("علت یا توضیح (اختیاری)") }, singleLine = true,
                    shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()
                )

                Spacer(Modifier.height(14.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(0.85f)) { Text("لغو") }
                    Button(
                        onClick = { onConfirm(formattedTime, note); onDismiss() },
                        colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = onAccent),
                        modifier = Modifier.weight(1.45f)
                    ) {
                        Text(
                            text = if (isLate) "ثبت تأخیر ${toPersianDigits(formattedTime)}" else "ثبت خروج ${toPersianDigits(formattedTime)}",
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
    count: Int, listState: LazyListState, label: String, accent: Color, fadeBg: Color, onValueChange: (Int) -> Unit
) {
    val itemH = 44.dp
    val halfPx = with(LocalDensity.current) { 22.dp.roundToPx() }
    val fling = rememberSnapFlingBehavior(lazyListState = listState)
    val haptic = LocalHapticFeedback.current

    val currentVal by remember {
        derivedStateOf {
            val boost = if (listState.firstVisibleItemScrollOffset >= halfPx) 1 else 0
            (listState.firstVisibleItemIndex + boost).coerceIn(0, count - 1)
        }
    }

    LaunchedEffect(currentVal) {
        onValueChange(currentVal)
        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
    }

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(4.dp))
        Box(modifier = Modifier.width(88.dp).height(itemH * 3), contentAlignment = Alignment.Center) {
            // قاب کپسولی برجسته ردیف انتخاب‌شده
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = accent.copy(alpha = 0.16f),
                border = BorderStroke(1.8.dp, accent),
                modifier = Modifier.fillMaxWidth().height(itemH)
            ) {}

            LazyColumn(state = listState, flingBehavior = fling, modifier = Modifier.fillMaxWidth().height(itemH * 3)) {
                item { Spacer(Modifier.height(itemH)) }
                items(count) { v ->
                    val isCenter = v == currentVal
                    val sc by animateFloatAsState(if (isCenter) 1.12f else 0.80f, spring(Spring.DampingRatioMediumBouncy), label = "wSc")
                    val al by animateFloatAsState(if (isCenter) 1f else 0.36f, label = "wAl")
                    Box(
                        modifier = Modifier.fillMaxWidth().height(itemH).graphicsLayer { scaleX = sc; scaleY = sc; alpha = al },
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = toPersianDigits(String.format("%02d", v)),
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = if (isCenter) FontWeight.ExtraBold else FontWeight.Medium,
                            color = if (isCenter) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                item { Spacer(Modifier.height(itemH)) }
            }

            // گرادیان محوکننده بالا و پایین برای حس چرخ استوانه‌ای سه‌بعدی
            Box(modifier = Modifier.align(Alignment.TopCenter).fillMaxWidth().height(36.dp).background(Brush.verticalGradient(listOf(fadeBg, Color.Transparent))))
            Box(modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().height(36.dp).background(Brush.verticalGradient(listOf(Color.Transparent, fadeBg))))
        }
    }
}
