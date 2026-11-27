package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
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
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.VerifiedUser
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.StudentAttendanceRow

@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    onStatusChange: (AttendanceStatus) -> Unit,
    onSendIndividualNotice: (StudentAttendanceRow, AttendanceStatus) -> Unit,
    onCallParent: (String) -> Unit,
    onEditStudent: (StudentAttendanceRow) -> Unit,
    onDeleteStudent: (StudentAttendanceRow) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val accentColor = statusPrimaryColor(student.currentStatus)

    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 5.dp),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.2.dp, accentColor.copy(alpha = 0.55f)),
        tonalElevation = 1.dp
    ) {
        Row(modifier = Modifier.fillMaxWidth().height(IntrinsicSize.Min)) {
            Box(modifier = Modifier.width(6.dp).fillMaxHeight().background(accentColor))

            Column(modifier = Modifier.weight(1f).padding(12.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(RoundedCornerShape(11.dp))
                            .background(MaterialTheme.colorScheme.primaryContainer),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = toPersianDigits(indexInClass.toString()),
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }

                    Spacer(Modifier.width(10.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "${student.firstName} ${student.lastName}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.onSurface,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        val meta = buildString {
                            if (student.fatherName.isNotBlank()) append("فرزند ${student.fatherName}")
                            if (student.mobile.isNotBlank()) {
                                if (isNotEmpty()) append(" · ")
                                append(toPersianDigits(student.mobile))
                            }
                        }
                        if (meta.isNotBlank()) {
                            Text(
                                text = meta,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        student.periodStatuses.forEachIndexed { i, st ->
                            val dotBg = if (st == AttendanceStatus.UNMARKED) {
                                MaterialTheme.colorScheme.surfaceContainerHighest
                            } else statusPrimaryColor(st)
                            val dotFg = if (st == AttendanceStatus.UNMARKED) {
                                MaterialTheme.colorScheme.onSurfaceVariant
                            } else statusOnColor(st)
                            Box(
                                modifier = Modifier.size(22.dp).clip(CircleShape).background(dotBg),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = toPersianDigits((i + 1).toString()),
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = dotFg
                                )
                            }
                        }
                    }
                }

                Spacer(Modifier.height(10.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    StatusActionChip("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, StatusColors.OnPresent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onStatusChange(AttendanceStatus.PRESENT)
                    }
                    StatusActionChip("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, StatusColors.OnAbsent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onStatusChange(AttendanceStatus.ABSENT)
                    }
                    StatusActionChip("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, StatusColors.OnLate, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onStatusChange(AttendanceStatus.LATE)
                    }
                    StatusActionChip("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, StatusColors.OnExcused, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onStatusChange(AttendanceStatus.EXCUSED)
                    }
                }

                Spacer(Modifier.height(8.dp))

                val canSendAbsent = student.currentStatus == AttendanceStatus.ABSENT
                val canSendLate = student.currentStatus == AttendanceStatus.LATE
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CompactActionBtn(
                        label = if (canSendLate) "پیام تأخیر" else "پیام غیبت",
                        icon = Icons.Rounded.Sms,
                        enabled = canSendAbsent || canSendLate,
                        highlightBg = if (canSendLate) StatusColors.Late else StatusColors.Absent,
                        highlightFg = if (canSendLate) StatusColors.OnLate else StatusColors.OnAbsent,
                        modifier = Modifier.weight(1.4f),
                        onClick = {
                            if (canSendAbsent) onSendIndividualNotice(student, AttendanceStatus.ABSENT)
                            else if (canSendLate) onSendIndividualNotice(student, AttendanceStatus.LATE)
                        }
                    )
                    CompactActionBtn(
                        label = "تماس",
                        icon = Icons.Rounded.Call,
                        enabled = student.mobile.isNotBlank(),
                        highlightBg = MaterialTheme.colorScheme.secondaryContainer,
                        highlightFg = MaterialTheme.colorScheme.onSecondaryContainer,
                        modifier = Modifier.weight(1f),
                        onClick = { onCallParent(student.mobile) }
                    )
                    CompactActionBtn(
                        label = "ویرایش",
                        icon = Icons.Rounded.Edit,
                        enabled = true,
                        highlightBg = MaterialTheme.colorScheme.surfaceContainerHigh,
                        highlightFg = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.weight(1f),
                        onClick = { onEditStudent(student) }
                    )
                    CompactActionBtn(
                        label = "حذف",
                        icon = Icons.Rounded.Delete,
                        enabled = true,
                        highlightBg = MaterialTheme.colorScheme.errorContainer,
                        highlightFg = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.weight(0.9f),
                        onClick = { onDeleteStudent(student) }
                    )
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
    activeBg: Color,
    activeFg: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg = if (selected) activeBg else MaterialTheme.colorScheme.surfaceContainerHigh
    val fg = if (selected) activeFg else MaterialTheme.colorScheme.onSurface
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(if (selected) 50 else 12))
            .background(bg)
            .clickable(onClick = onClick)
            .padding(vertical = 8.dp, horizontal = 3.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(14.dp))
        Spacer(Modifier.width(3.dp))
        Text(text = label, style = MaterialTheme.typography.labelMedium, fontWeight = if (selected) FontWeight.ExtraBold else FontWeight.SemiBold, color = fg, maxLines = 1)
    }
}

@Composable
private fun CompactActionBtn(
    label: String,
    icon: ImageVector,
    enabled: Boolean,
    highlightBg: Color,
    highlightFg: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg = if (enabled) highlightBg else MaterialTheme.colorScheme.surfaceContainer
    val fg = if (enabled) highlightFg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f)
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(10.dp))
            .background(bg)
            .clickable(enabled = enabled, onClick = onClick)
            .padding(vertical = 7.dp, horizontal = 4.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(14.dp))
        Spacer(Modifier.width(3.dp))
        Text(text = label, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = fg, maxLines = 1)
    }
}

fun statusPrimaryColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.PRESENT -> StatusColors.Present
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    AttendanceStatus.UNMARKED -> StatusColors.Unmarked
}

fun statusOnColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.PRESENT -> StatusColors.OnPresent
    AttendanceStatus.ABSENT -> StatusColors.OnAbsent
    AttendanceStatus.LATE -> StatusColors.OnLate
    AttendanceStatus.EXCUSED -> StatusColors.OnExcused
    AttendanceStatus.UNMARKED -> Color.White
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) {
        for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c)
    }
}
