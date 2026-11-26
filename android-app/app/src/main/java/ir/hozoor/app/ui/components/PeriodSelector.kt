package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
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
fun PeriodSelector(
    selectedPeriod: Period,
    onSelectPeriod: (Period) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
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
                onCheckedChange = {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onSelectPeriod(period)
                },
                modifier = Modifier.weight(1f),
                shapes = shapes,
                colors = ToggleButtonDefaults.toggleButtonColors(
                    checkedContainerColor = MaterialTheme.colorScheme.primary,
                    checkedContentColor = MaterialTheme.colorScheme.onPrimary,
                    containerColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                    contentColor = MaterialTheme.colorScheme.onSurfaceVariant
                )
            ) {
                if (checked) {
                    Icon(Icons.Rounded.NotificationsActive, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                }
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = if (checked) FontWeight.Bold else FontWeight.Medium,
                    maxLines = 1
                )
            }
        }
    }
}
