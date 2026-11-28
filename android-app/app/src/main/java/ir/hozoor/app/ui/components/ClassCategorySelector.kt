package ir.hozoor.app.ui.components

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
