package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.snapping.rememberSnapFlingBehavior
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.StudentAttendanceRow
import java.time.LocalTime

private val EXIT_REASONS = listOf("برنگشت", "با اجازه", "دفتر / معاون", "بهداشت / آبخوری")

/** دیالوگ ساده و سریع ثبت خروج از کلاس با چرخ اسکرول ساعت و دقیقه (پیش‌فرض روی ساعت لحظه‌ای گوشی) */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ExitTimeWheelDialog(
    student: StudentAttendanceRow,
    onConfirm: (exitTime: String, reason: String) -> Unit,
    onDismiss: () -> Unit
) {
    val now = remember { LocalTime.now() }
    val initParts = remember(student.exitTime) {
        val sp = student.exitTime.split(":")
        val h = sp.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: now.hour
        val m = sp.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: now.minute
        h to m
    }
    var selectedHour by remember { mutableIntStateOf(initParts.first) }
    var selectedMinute by remember { mutableIntStateOf(initParts.second) }
    var note by remember { mutableStateOf(student.note.ifBlank { "برنگشت" }) }

    val formattedTime = String.format("%02d:%02d", selectedHour, selectedMinute)

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(28.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, tonalElevation = 6.dp) {
            Column(modifier = Modifier.padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("ثبت خروج از کلاس", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold, color = StatusColors.LeftClass)
                Spacer(Modifier.height(2.dp))
                Text("${student.firstName} ${student.lastName}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(Modifier.height(14.dp))

                // چرخ اسکرول ساعت و دقیقه (چپ به راست برای خوانش استاندارد ساعت ۰۹:۴۲)
                CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) {
                        NumberWheel(count = 24, initialValue = initParts.first, label = "ساعت", onValueChange = { selectedHour = it })
                        Text(":", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.ExtraBold, modifier = Modifier.padding(horizontal = 10.dp))
                        NumberWheel(count = 60, initialValue = initParts.second, label = "دقیقه", onValueChange = { selectedMinute = it })
                    }
                }

                Spacer(Modifier.height(14.dp))

                // چیپ‌های آماده برای سرعت بالا سر کلاس
                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.fillMaxWidth()) {
                    EXIT_REASONS.forEach { reason ->
                        FilterChip(
                            selected = note == reason,
                            onClick = { note = reason },
                            label = { Text(reason, style = MaterialTheme.typography.labelMedium) }
                        )
                    }
                }

                Spacer(Modifier.height(6.dp))
                OutlinedTextField(
                    value = note,
                    onValueChange = { note = it },
                    label = { Text("توضیح اختیاری") },
                    singleLine = true,
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(Modifier.height(14.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(0.9f)) { Text("لغو") }
                    Button(
                        onClick = { onConfirm(formattedTime, note); onDismiss() },
                        colors = ButtonDefaults.buttonColors(containerColor = StatusColors.LeftClass, contentColor = StatusColors.OnLeftClass),
                        modifier = Modifier.weight(1.4f)
                    ) {
                        Text("ثبت خروج ${toPersianDigits(formattedTime)}", fontWeight = FontWeight.ExtraBold)
                    }
                }
            }
        }
    }
}

@Composable
private fun NumberWheel(count: Int, initialValue: Int, label: String, onValueChange: (Int) -> Unit) {
    val itemHeight = 44.dp
    val halfPx = with(LocalDensity.current) { 22.dp.roundToPx() }
    val listState = rememberLazyListState(initialFirstVisibleItemIndex = initialValue.coerceIn(0, count - 1))
    val fling = rememberSnapFlingBehavior(lazyListState = listState)
    val haptic = LocalHapticFeedback.current

    val currentVal by remember {
        derivedStateOf {
            val offsetBoost = if (listState.firstVisibleItemScrollOffset >= halfPx) 1 else 0
            (listState.firstVisibleItemIndex + offsetBoost).coerceIn(0, count - 1)
        }
    }

    LaunchedEffect(currentVal) {
        onValueChange(currentVal)
        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
    }

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(4.dp))
        Box(modifier = Modifier.width(84.dp).height(itemHeight * 3), contentAlignment = Alignment.Center) {
            // نوار برجسته ردیف وسط
            Surface(
                shape = RoundedCornerShape(14.dp),
                color = StatusColors.LeftClass.copy(alpha = 0.14f),
                border = BorderStroke(1.5.dp, StatusColors.LeftClass.copy(alpha = 0.6f)),
                modifier = Modifier.fillMaxWidth().height(itemHeight)
            ) {}

            LazyColumn(state = listState, flingBehavior = fling, modifier = Modifier.fillMaxWidth().height(itemHeight * 3)) {
                item { Spacer(Modifier.height(itemHeight)) }
                items(count) { v ->
                    val isCenter = v == currentVal
                    Box(modifier = Modifier.fillMaxWidth().height(itemHeight), contentAlignment = Alignment.Center) {
                        Text(
                            text = toPersianDigits(String.format("%02d", v)),
                            style = if (isCenter) MaterialTheme.typography.headlineSmall else MaterialTheme.typography.titleMedium,
                            fontWeight = if (isCenter) FontWeight.ExtraBold else FontWeight.Normal,
                            color = if (isCenter) StatusColors.LeftClass else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f)
                        )
                    }
                }
                item { Spacer(Modifier.height(itemHeight)) }
            }
        }
    }
}
