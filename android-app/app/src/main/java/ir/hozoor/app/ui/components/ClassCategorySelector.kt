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

/** دسته‌بندی بدون بخش اضافه مدرسه، با نام کامل رشته‌ها (۲ خطی بدون ...)، نمایش دائمی شعبه و انیمیشن فنری */
@Composable
fun ClassCategorySelector(
    majors: List<String>,
    selectedMajor: String,
    grades: List<String>,
    selectedGrade: String,
    sections: List<Int>,
    selectedSection: Int,
    onSelectMajor: (String) -> Unit,
    onSelectGrade: (String) -> Unit,
    onSelectSection: (Int) -> Unit,
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
                AnimatedCategoryGrid(
                    title = "رشته",
                    items = majors,
                    selected = selectedMajor,
                    labelOf = { it },
                    itemHeight = 52.dp,
                    maxLines = 2,
                    selectedBg = MaterialTheme.colorScheme.primary,
                    selectedFg = MaterialTheme.colorScheme.onPrimary,
                    unselectedBg = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.48f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectMajor
                )
            }
            if (grades.isNotEmpty()) {
                AnimatedCategoryGrid(
                    title = "پایه",
                    items = grades,
                    selected = selectedGrade,
                    labelOf = { it },
                    itemHeight = 44.dp,
                    maxLines = 1,
                    selectedBg = MaterialTheme.colorScheme.secondary,
                    selectedFg = MaterialTheme.colorScheme.onSecondary,
                    unselectedBg = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectGrade
                )
            }
            if (sections.isNotEmpty()) {
                AnimatedCategoryGrid(
                    title = "شعبه",
                    items = sections,
                    selected = selectedSection,
                    labelOf = { "شعبه ${toPersianDigits(it.toString())}" },
                    itemHeight = 42.dp,
                    maxLines = 1,
                    selectedBg = MaterialTheme.colorScheme.tertiary,
                    selectedFg = MaterialTheme.colorScheme.onTertiary,
                    unselectedBg = MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.55f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectSection
                )
            }
        }
    }
}

@Composable
private fun <T> AnimatedCategoryGrid(
    title: String,
    items: List<T>,
    selected: T,
    labelOf: (T) -> String,
    itemHeight: Dp,
    maxLines: Int,
    selectedBg: Color,
    selectedFg: Color,
    unselectedBg: Color,
    unselectedFg: Color,
    onSelect: (T) -> Unit
) {
    val haptic = LocalHapticFeedback.current
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 5.dp, start = 2.dp)
        )
        Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
            items.chunked(3).forEach { chunk ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    chunk.forEach { item ->
                        val isSelected = item == selected
                        val bg by animateColorAsState(
                            targetValue = if (isSelected) selectedBg else unselectedBg,
                            animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
                            label = "catBg"
                        )
                        val fg by animateColorAsState(
                            targetValue = if (isSelected) selectedFg else unselectedFg,
                            animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
                            label = "catFg"
                        )
                        val corner by animateDpAsState(
                            targetValue = if (isSelected) 22.dp else 13.dp,
                            animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
                            label = "catCorner"
                        )
                        val scale by animateFloatAsState(
                            targetValue = if (isSelected) 1.03f else 0.98f,
                            animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
                            label = "catScale"
                        )

                        Surface(
                            onClick = {
                                haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                onSelect(item)
                            },
                            shape = RoundedCornerShape(corner),
                            color = bg,
                            tonalElevation = if (isSelected) 4.dp else 0.dp,
                            shadowElevation = if (isSelected) 3.dp else 0.dp,
                            modifier = Modifier
                                .weight(1f)
                                .height(itemHeight)
                                .graphicsLayer { scaleX = scale; scaleY = scale }
                        ) {
                            Box(contentAlignment = Alignment.Center, modifier = Modifier.fillMaxSize().padding(horizontal = 6.dp, vertical = 4.dp)) {
                                Text(
                                    text = labelOf(item),
                                    style = MaterialTheme.typography.labelLarge,
                                    fontWeight = if (isSelected) FontWeight.ExtraBold else FontWeight.SemiBold,
                                    color = fg,
                                    maxLines = maxLines,
                                    textAlign = TextAlign.Center,
                                    lineHeight = MaterialTheme.typography.labelLarge.lineHeight
                                )
                            }
                        }
                    }
                    repeat(3 - chunk.size) { Spacer(Modifier.weight(1f)) }
                }
            }
        }
    }
}
