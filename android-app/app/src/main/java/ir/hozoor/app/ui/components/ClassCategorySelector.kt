package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

@Composable
fun ClassCategorySelector(
    schools: List<String>,
    selectedSchool: String,
    majors: List<String>,
    selectedMajor: String,
    grades: List<String>,
    selectedGrade: String,
    sections: List<Int>,
    selectedSection: Int,
    onSelectSchool: (String) -> Unit,
    onSelectMajor: (String) -> Unit,
    onSelectGrade: (String) -> Unit,
    onSelectSection: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            if (schools.size > 1) {
                CategoryGridRow(
                    title = "مدرسه",
                    items = schools,
                    selected = selectedSchool,
                    labelOf = { it },
                    selectedBg = MaterialTheme.colorScheme.primary,
                    selectedFg = MaterialTheme.colorScheme.onPrimary,
                    unselectedBg = MaterialTheme.colorScheme.surfaceContainerHigh,
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectSchool
                )
            }
            if (majors.isNotEmpty()) {
                CategoryGridRow(
                    title = "رشته",
                    items = majors,
                    selected = selectedMajor,
                    labelOf = { it },
                    selectedBg = MaterialTheme.colorScheme.primary,
                    selectedFg = MaterialTheme.colorScheme.onPrimary,
                    unselectedBg = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.45f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectMajor
                )
            }
            if (grades.isNotEmpty()) {
                CategoryGridRow(
                    title = "پایه",
                    items = grades,
                    selected = selectedGrade,
                    labelOf = { it },
                    selectedBg = MaterialTheme.colorScheme.secondary,
                    selectedFg = MaterialTheme.colorScheme.onSecondary,
                    unselectedBg = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectGrade
                )
            }
            if (sections.size > 1) {
                CategoryGridRow(
                    title = "شعبه",
                    items = sections,
                    selected = selectedSection,
                    labelOf = { "شعبه ${toPersianDigits(it.toString())}" },
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
private fun <T> CategoryGridRow(
    title: String,
    items: List<T>,
    selected: T,
    labelOf: (T) -> String,
    selectedBg: Color,
    selectedFg: Color,
    unselectedBg: Color,
    unselectedFg: Color,
    onSelect: (T) -> Unit
) {
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 4.dp, start = 2.dp)
        )
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            items.chunked(3).forEach { chunk ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    chunk.forEach { item ->
                        val isSelected = item == selected
                        Surface(
                            onClick = { onSelect(item) },
                            shape = RoundedCornerShape(14.dp),
                            color = if (isSelected) selectedBg else unselectedBg,
                            border = if (isSelected) BorderStroke(2.dp, MaterialTheme.colorScheme.outline) else null,
                            modifier = Modifier.weight(1f).height(42.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center,
                                modifier = Modifier.padding(horizontal = 6.dp)
                            ) {
                                Text(
                                    text = labelOf(item),
                                    style = MaterialTheme.typography.labelLarge,
                                    fontWeight = if (isSelected) FontWeight.ExtraBold else FontWeight.SemiBold,
                                    color = if (isSelected) selectedFg else unselectedFg,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                    textAlign = TextAlign.Center
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
