package ir.hozoor.app.ui.components

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

private val WEEK_HEADERS = listOf("ش", "ی", "د", "س", "چ", "پ", "ج")

@Composable
fun JalaliDatePickerDialog(
    initialYear: Int, initialMonth: Int, selectedIso: String,
    gridProvider: (Int, Int) -> JalaliMonthGrid, onSelectIso: (String) -> Unit, onDismiss: () -> Unit
) {
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
                    WEEK_HEADERS.forEachIndexed { idx, w ->
                        Text(w, modifier = Modifier.weight(1f), textAlign = TextAlign.Center, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.ExtraBold, color = if (idx == 6) StatusColors.Absent else MaterialTheme.colorScheme.primary)
                    }
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
                                    ) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Text(toPersianDigits(cell.day.toString()), style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = when { isSel -> MaterialTheme.colorScheme.onPrimary; cell.isFriday -> StatusColors.Absent; else -> MaterialTheme.colorScheme.onSurface })
                                        }
                                    }
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
