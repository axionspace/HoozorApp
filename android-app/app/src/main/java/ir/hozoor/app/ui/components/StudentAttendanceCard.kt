package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
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
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.VerifiedUser
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalIconButton
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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.StudentAttendanceRow

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    onStatusChange: (AttendanceStatus) -> Unit,
    onSendSms: (StudentAttendanceRow) -> Unit,
    onCallParent: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val cardCorner by animateDpAsState(
        targetValue = if (student.currentStatus == AttendanceStatus.UNMARKED) 18.dp else 28.dp,
        animationSpec = MaterialTheme.motionScheme.fastSpatialSpec(),
        label = "cardCorner"
    )

    val containerTint = when (student.currentStatus) {
        AttendanceStatus.PRESENT -> StatusColors.PresentContainer.copy(alpha = 0.45f)
        AttendanceStatus.ABSENT -> StatusColors.AbsentContainer.copy(alpha = 0.55f)
        AttendanceStatus.LATE -> StatusColors.LateContainer.copy(alpha = 0.50f)
        AttendanceStatus.EXCUSED -> StatusColors.ExcusedContainer.copy(alpha = 0.50f)
        AttendanceStatus.UNMARKED -> MaterialTheme.colorScheme.surfaceContainerLow
    }

    Surface(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 5.dp),
        shape = RoundedCornerShape(cardCorner),
        color = containerTint,
        tonalElevation = 1.dp
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(14.dp))
                        .background(statusPrimaryColor(student.currentStatus).copy(alpha = 0.16f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = toPersianDigits(indexInClass.toString()),
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = statusPrimaryColor(student.currentStatus)
                    )
                }

                Spacer(Modifier.width(12.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "${student.firstName} ${student.lastName}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "فرزند ${student.fatherName}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    student.periodStatuses.forEachIndexed { i, st ->
                        Box(
                            modifier = Modifier
                                .size(22.dp)
                                .clip(CircleShape)
                                .background(statusPrimaryColor(st).copy(alpha = 0.22f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = toPersianDigits((i + 1).toString()),
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = statusPrimaryColor(st)
                            )
                        }
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                StatusActionChip("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onStatusChange(AttendanceStatus.PRESENT)
                }
                StatusActionChip("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onStatusChange(AttendanceStatus.ABSENT)
                }
                StatusActionChip("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onStatusChange(AttendanceStatus.LATE)
                }
                StatusActionChip("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onStatusChange(AttendanceStatus.EXCUSED)
                }
            }

            AnimatedVisibility(
                visible = (student.currentStatus == AttendanceStatus.ABSENT ||
                    student.currentStatus == AttendanceStatus.LATE) && student.mobile.isNotBlank()
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 10.dp),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = toPersianDigits(student.mobile),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f)
                    )
                    FilledTonalIconButton(onClick = { onCallParent(student.mobile) }) {
                        Icon(Icons.Rounded.Call, contentDescription = "تماس با ولی")
                    }
                    Spacer(Modifier.width(6.dp))
                    FilledTonalIconButton(onClick = { onSendSms(student) }) {
                        Icon(Icons.Rounded.Sms, contentDescription = "ارسال پیامک به ولی")
                    }
                }
            }
        }
    }
}

@Composable
private fun StatusActionChip(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    activeColor: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg = if (selected) activeColor else MaterialTheme.colorScheme.surface.copy(alpha = 0.85f)
    val fg = if (selected) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(if (selected) 50 else 14))
            .background(bg)
            .clickable(onClick = onClick)
            .padding(vertical = 8.dp, horizontal = 4.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(15.dp))
        Spacer(Modifier.width(3.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
            color = fg,
            maxLines = 1
        )
    }
}

fun statusPrimaryColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.PRESENT -> StatusColors.Present
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    AttendanceStatus.UNMARKED -> StatusColors.Unmarked
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) {
        for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c)
    }
}
