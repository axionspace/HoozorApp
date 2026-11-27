package ir.hozoor.app.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.BorderStroke
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
import androidx.compose.material.icons.rounded.Delete
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.Grade
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.VerifiedUser
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
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.StudentAttendanceRow

/** کارت مدرن Material 3 Expressive با انیمیشن فنری و دایره‌های تعاملی ۱ تا ۴ (پیش‌فرض سبز -> قرمز -> زرد -> آبی) */
@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    selectedPeriod: Period,
    onStatusChange: (AttendanceStatus) -> Unit,
    onCyclePeriodDot: (periodIndex: Int) -> Unit,
    onSendIndividualNotice: (StudentAttendanceRow, AttendanceStatus) -> Unit,
    onCallParent: (String) -> Unit,
    onQuickScore: (StudentAttendanceRow) -> Unit,
    onEditStudent: (StudentAttendanceRow) -> Unit,
    onDeleteStudent: (StudentAttendanceRow) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val accentColor by animateColorAsState(
        targetValue = statusPrimaryColor(student.currentStatus),
        animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
        label = "accent"
    )
    val selectedPeriodIdx = when (selectedPeriod) {
        Period.FIRST -> 0
        Period.SECOND -> 1
        Period.THIRD -> 2
        Period.FOURTH -> 3
    }

    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(26.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.2.dp, accentColor.copy(alpha = 0.42f)),
        shadowElevation = 2.dp,
        tonalElevation = 2.dp
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            // ردیف بالایی: آواتار شماره، نام دانش‌آموز و ۴ دایره تعاملی زنگ‌ها (۱ ۲ ۳ ۴)
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Surface(
                    shape = CircleShape,
                    color = accentColor.copy(alpha = 0.14f),
                    border = BorderStroke(2.dp, accentColor),
                    modifier = Modifier.size(42.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            text = toPersianDigits(indexInClass.toString()),
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.ExtraBold,
                            color = accentColor
                        )
                    }
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
                        if (student.classScore.isNotBlank()) {
                            if (isNotEmpty()) append(" • ")
                            append("نمره: ${toPersianDigits(student.classScore)}")
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

                // عددهای ۱ ۲ ۳ ۴: به صورت عادی همه سبز (حاضر)، با هر لمس: سبز -> قرمز -> زرد -> آبی
                Row(horizontalArrangement = Arrangement.spacedBy(5.dp), verticalAlignment = Alignment.CenterVertically) {
                    for (i in 0..3) {
                        val rawSt = student.periodStatuses.getOrElse(i) { AttendanceStatus.UNMARKED }
                        val effectiveSt = if (rawSt == AttendanceStatus.UNMARKED) AttendanceStatus.PRESENT else rawSt
                        val isActiveBell = i == selectedPeriodIdx
                        val dotBg by animateColorAsState(
                            targetValue = statusPrimaryColor(effectiveSt),
                            animationSpec = spring(stiffness = Spring.StiffnessMedium),
                            label = "dotBg$i"
                        )
                        val dotFg by animateColorAsState(
                            targetValue = statusOnColor(effectiveSt),
                            animationSpec = spring(stiffness = Spring.StiffnessMedium),
                            label = "dotFg$i"
                        )
                        val dotScale by animateFloatAsState(
                            targetValue = if (isActiveBell) 1.12f else 0.96f,
                            animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy),
                            label = "dotScale$i"
                        )
                        Surface(
                            onClick = {
                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                onCyclePeriodDot(i)
                            },
                            shape = CircleShape,
                            color = dotBg,
                            border = if (isActiveBell) BorderStroke(2.dp, MaterialTheme.colorScheme.onSurface) else null,
                            modifier = Modifier
                                .size(28.dp)
                                .graphicsLayer { scaleX = dotScale; scaleY = dotScale }
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = toPersianDigits((i + 1).toString()),
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = dotFg
                                )
                            }
                        }
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            // ردیف ۴ دکمه وضعیت با انیمیشن تغییر رنگ، تغییر شکل و پرش فنری
            Surface(
                shape = RoundedCornerShape(18.dp),
                color = MaterialTheme.colorScheme.surfaceContainer,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(4.dp),
                    horizontalArrangement = Arrangement.spacedBy(5.dp)
                ) {
                    AnimatedStatusPill("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, StatusColors.OnPresent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onStatusChange(AttendanceStatus.PRESENT)
                    }
                    AnimatedStatusPill("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, StatusColors.OnAbsent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onStatusChange(AttendanceStatus.ABSENT)
                    }
                    AnimatedStatusPill("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, StatusColors.OnLate, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onStatusChange(AttendanceStatus.LATE)
                    }
                    AnimatedStatusPill("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, StatusColors.OnExcused, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onStatusChange(AttendanceStatus.EXCUSED)
                    }
                }
            }

            Spacer(Modifier.height(10.dp))

            // ردیف ابزارهای زیر کارت: پیامک، نمره، تماس، ویرایش، حذف
            val isAbsent = student.currentStatus == AttendanceStatus.ABSENT
            val isLate = student.currentStatus == AttendanceStatus.LATE
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                ActionPill(
                    label = if (isLate) "پیام تأخیر" else "پیام غیبت",
                    icon = Icons.Rounded.Sms,
                    enabled = isAbsent || isLate,
                    bg = if (isLate) StatusColors.Late else StatusColors.Absent,
                    fg = if (isLate) StatusColors.OnLate else StatusColors.OnAbsent,
                    modifier = Modifier.weight(1.45f)
                ) {
                    if (isAbsent) onSendIndividualNotice(student, AttendanceStatus.ABSENT)
                    else if (isLate) onSendIndividualNotice(student, AttendanceStatus.LATE)
                }
                ActionPill(
                    label = if (student.classScore.isNotBlank()) toPersianDigits(student.classScore) else "نمره",
                    icon = Icons.Rounded.Grade,
                    enabled = true,
                    bg = MaterialTheme.colorScheme.tertiaryContainer,
                    fg = MaterialTheme.colorScheme.onTertiaryContainer,
                    modifier = Modifier.weight(0.95f)
                ) { onQuickScore(student) }
                IconActionCircle(Icons.Rounded.Call, "تماس", student.mobile.isNotBlank(), MaterialTheme.colorScheme.secondaryContainer, MaterialTheme.colorScheme.onSecondaryContainer) {
                    onCallParent(student.mobile)
                }
                IconActionCircle(Icons.Rounded.Edit, "ویرایش", true, MaterialTheme.colorScheme.surfaceContainerHigh, MaterialTheme.colorScheme.onSurface) {
                    onEditStudent(student)
                }
                IconActionCircle(Icons.Rounded.Delete, "حذف", true, MaterialTheme.colorScheme.errorContainer, MaterialTheme.colorScheme.onErrorContainer) {
                    onDeleteStudent(student)
                }
            }
        }
    }
}

@Composable
private fun AnimatedStatusPill(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    activeBg: Color,
    activeFg: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg by animateColorAsState(
        targetValue = if (selected) activeBg else Color.Transparent,
        animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
        label = "stBg"
    )
    val fg by animateColorAsState(
        targetValue = if (selected) activeFg else MaterialTheme.colorScheme.onSurfaceVariant,
        animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
        label = "stFg"
    )
    val corner by animateDpAsState(
        targetValue = if (selected) 24.dp else 10.dp,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
        label = "stCorner"
    )
    val scale by animateFloatAsState(
        targetValue = if (selected) 1.03f else 0.96f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
        label = "stScale"
    )

    Row(
        modifier = modifier
            .graphicsLayer { scaleX = scale; scaleY = scale }
            .clip(RoundedCornerShape(corner))
            .background(bg)
            .clickable(onClick = onClick)
            .padding(vertical = 9.dp, horizontal = 3.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(15.dp))
        Spacer(Modifier.width(3.dp))
        Text(label, style = MaterialTheme.typography.labelMedium, fontWeight = if (selected) FontWeight.ExtraBold else FontWeight.SemiBold, color = fg, maxLines = 1)
    }
}

@Composable
private fun ActionPill(label: String, icon: ImageVector, enabled: Boolean, bg: Color, fg: Color, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val actualBg by animateColorAsState(if (enabled) bg else MaterialTheme.colorScheme.surfaceContainer, label = "actBg")
    val actualFg by animateColorAsState(if (enabled) fg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f), label = "actFg")
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(14.dp))
            .background(actualBg)
            .clickable(enabled = enabled, onClick = onClick)
            .padding(vertical = 8.dp, horizontal = 6.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = actualFg, modifier = Modifier.size(15.dp))
        Spacer(Modifier.width(4.dp))
        Text(label, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.ExtraBold, color = actualFg, maxLines = 1)
    }
}

@Composable
private fun IconActionCircle(icon: ImageVector, desc: String, enabled: Boolean, bg: Color, fg: Color, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        enabled = enabled,
        shape = CircleShape,
        color = if (enabled) bg else MaterialTheme.colorScheme.surfaceContainer,
        modifier = Modifier.size(34.dp)
    ) {
        Box(contentAlignment = Alignment.Center) {
            Icon(icon, contentDescription = desc, tint = if (enabled) fg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f), modifier = Modifier.size(17.dp))
        }
    }
}

fun statusPrimaryColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    else -> StatusColors.Present
}

fun statusOnColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.ABSENT -> StatusColors.OnAbsent
    AttendanceStatus.LATE -> StatusColors.OnLate
    AttendanceStatus.EXCUSED -> StatusColors.OnExcused
    else -> StatusColors.OnPresent
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) {
        for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c)
    }
}
