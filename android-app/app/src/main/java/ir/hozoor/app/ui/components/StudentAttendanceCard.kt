package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
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
import androidx.compose.material.icons.rounded.DirectionsRun
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
import androidx.compose.ui.unit.sp
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.StudentAttendanceRow

/** کارت مدرن با دایره‌های کوچک غیرکلیکی ۱ تا ۴ (حاشیه سفید برای زنگ فعال، بدون بریدن نام دانش‌آموز) + وضعیت خروج از کلاس */
@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    selectedPeriod: Period,
    onStatusChange: (AttendanceStatus) -> Unit,
    onRequestLeftClass: () -> Unit,
    onSendIndividualNotice: (StudentAttendanceRow, AttendanceStatus) -> Unit,
    onCallParent: (String) -> Unit,
    onQuickGrade: (StudentAttendanceRow) -> Unit,
    onEditStudent: (StudentAttendanceRow) -> Unit,
    onDeleteStudent: (StudentAttendanceRow) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val accentColor by animateColorAsState(statusPrimaryColor(student.currentStatus), spring(stiffness = Spring.StiffnessMediumLow), label = "acc")
    val activeIdx = when (selectedPeriod) { Period.FIRST -> 0; Period.SECOND -> 1; Period.THIRD -> 2; Period.FOURTH -> 3 }

    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.2.dp, accentColor.copy(alpha = 0.45f)),
        shadowElevation = 2.dp,
        tonalElevation = 2.dp
    ) {
        Column(modifier = Modifier.padding(13.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Surface(shape = CircleShape, color = accentColor.copy(alpha = 0.14f), border = BorderStroke(2.dp, accentColor), modifier = Modifier.size(36.dp)) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(toPersianDigits(indexInClass.toString()), style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.ExtraBold, color = accentColor)
                    }
                }
                Spacer(Modifier.width(9.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "${student.firstName} ${student.lastName}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.ExtraBold,
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                    val meta = buildString {
                        if (student.fatherName.isNotBlank()) append("فرزند ${student.fatherName}")
                        if (student.latestGrade.isNotBlank()) {
                            if (isNotEmpty()) append(" • ")
                            append("آخرین نمره: ${toPersianDigits(student.latestGrade)}")
                        }
                    }
                    if (meta.isNotBlank()) {
                        Text(meta, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                }

                Spacer(Modifier.width(6.dp))

                // عددهای کوچک ۱ تا ۴ (غیرکلیکی، حاشیه سفید روی زنگ فعال، بدون اشغال فضای نام)
                Row(horizontalArrangement = Arrangement.spacedBy(3.dp), verticalAlignment = Alignment.CenterVertically) {
                    for (i in 0..3) {
                        val raw = student.periodStatuses.getOrElse(i) { AttendanceStatus.UNMARKED }
                        val eff = if (raw == AttendanceStatus.UNMARKED) AttendanceStatus.PRESENT else raw
                        val isAct = i == activeIdx
                        val dotBg by animateColorAsState(statusPrimaryColor(eff), spring(stiffness = Spring.StiffnessMedium), label = "db$i")
                        val dotFg by animateColorAsState(statusOnColor(eff), spring(stiffness = Spring.StiffnessMedium), label = "df$i")
                        Surface(
                            shape = CircleShape,
                            color = dotBg,
                            border = if (isAct) BorderStroke(1.8.dp, Color.White) else null,
                            shadowElevation = if (isAct) 2.dp else 0.dp,
                            modifier = Modifier.size(if (isAct) 22.dp else 19.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(toPersianDigits((i + 1).toString()), fontSize = 10.sp, fontWeight = FontWeight.ExtraBold, color = dotFg)
                            }
                        }
                    }
                }
            }

            // نمایش برچسب ساعت خروج از کلاس (قابل لمس برای ویرایش ساعت خروج)
            AnimatedVisibility(visible = student.currentStatus == AttendanceStatus.LeftClass) {
                Surface(
                    onClick = onRequestLeftClass,
                    shape = RoundedCornerShape(12.dp),
                    color = StatusColors.LeftClass.copy(alpha = 0.14f),
                    border = BorderStroke(1.dp, StatusColors.LeftClass.copy(alpha = 0.5f)),
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp)
                ) {
                    Row(modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.DirectionsRun, null, tint = StatusColors.LeftClass, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        val info = buildString {
                            append("خروج از کلاس")
                            if (student.exitTime.isNotBlank()) append(" ساعت ${toPersianDigits(student.exitTime)}")
                            if (student.note.isNotBlank()) append(" (${student.note})")
                        }
                        Text(info, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = StatusColors.LeftClass, modifier = Modifier.weight(1f))
                        Text("تغییر ساعت", style = MaterialTheme.typography.labelSmall, color = StatusColors.LeftClass)
                    }
                }
            }

            Spacer(Modifier.height(10.dp))

            // ۵ وضعیت با انیمیشن فنری: حاضر، غایب، تأخیر، موجه، خروج
            Surface(shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.fillMaxWidth()) {
                Row(modifier = Modifier.fillMaxWidth().padding(3.dp), horizontalArrangement = Arrangement.spacedBy(3.dp)) {
                    AnimatedStatusPill("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, StatusColors.OnPresent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onStatusChange(AttendanceStatus.PRESENT)
                    }
                    AnimatedStatusPill("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, StatusColors.OnAbsent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onStatusChange(AttendanceStatus.ABSENT)
                    }
                    AnimatedStatusPill("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, StatusColors.OnLate, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove); onStatusChange(AttendanceStatus.LATE)
                    }
                    AnimatedStatusPill("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, StatusColors.OnExcused, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove); onStatusChange(AttendanceStatus.EXCUSED)
                    }
                    AnimatedStatusPill("خروج", Icons.Rounded.DirectionsRun, student.currentStatus == AttendanceStatus.LeftClass, StatusColors.LeftClass, StatusColors.OnLeftClass, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress); onRequestLeftClass()
                    }
                }
            }

            Spacer(Modifier.height(9.dp))

            val canNotify = student.currentStatus in listOf(AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.LeftClass)
            val notifyLabel = when (student.currentStatus) {
                AttendanceStatus.LATE -> "پیام تأخیر"
                AttendanceStatus.LeftClass -> "پیام خروج"
                else -> "پیام غیبت"
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                ActionPill(notifyLabel, Icons.Rounded.Sms, canNotify, accentColor, statusOnColor(student.currentStatus), Modifier.weight(1.4f)) {
                    onSendIndividualNotice(student, student.currentStatus)
                }
                ActionPill("نمره", Icons.Rounded.Grade, true, MaterialTheme.colorScheme.tertiaryContainer, MaterialTheme.colorScheme.onTertiaryContainer, Modifier.weight(0.9f)) {
                    onQuickGrade(student)
                }
                IconCircle(Icons.Rounded.Call, "تماس", student.mobile.isNotBlank(), MaterialTheme.colorScheme.secondaryContainer, MaterialTheme.colorScheme.onSecondaryContainer) { onCallParent(student.mobile) }
                IconCircle(Icons.Rounded.Edit, "ویرایش", true, MaterialTheme.colorScheme.surfaceContainerHigh, MaterialTheme.colorScheme.onSurface) { onEditStudent(student) }
                IconCircle(Icons.Rounded.Delete, "حذف", true, MaterialTheme.colorScheme.errorContainer, MaterialTheme.colorScheme.onErrorContainer) { onDeleteStudent(student) }
            }
        }
    }
}

@Composable
private fun AnimatedStatusPill(label: String, icon: ImageVector, selected: Boolean, activeBg: Color, activeFg: Color, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val bg by animateColorAsState(if (selected) activeBg else Color.Transparent, spring(stiffness = Spring.StiffnessMediumLow), label = "sBg")
    val fg by animateColorAsState(if (selected) activeFg else MaterialTheme.colorScheme.onSurfaceVariant, spring(stiffness = Spring.StiffnessMediumLow), label = "sFg")
    val corner by animateDpAsState(if (selected) 20.dp else 10.dp, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "sCr")
    val scale by animateFloatAsState(if (selected) 1.04f else 0.96f, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "sSc")

    Column(
        modifier = modifier.graphicsLayer { scaleX = scale; scaleY = scale }.clip(RoundedCornerShape(corner)).background(bg).clickable(onClick = onClick).padding(vertical = 6.dp, horizontal = 2.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(icon, label, tint = fg, modifier = Modifier.size(15.dp))
        Text(label, fontSize = 11.sp, fontWeight = if (selected) FontWeight.ExtraBold else FontWeight.SemiBold, color = fg, maxLines = 1, softWrap = false)
    }
}

@Composable
private fun ActionPill(label: String, icon: ImageVector, enabled: Boolean, bg: Color, fg: Color, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val aBg by animateColorAsState(if (enabled) bg else MaterialTheme.colorScheme.surfaceContainer, label = "aBg")
    val aFg by animateColorAsState(if (enabled) fg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f), label = "aFg")
    Row(
        modifier = modifier.clip(RoundedCornerShape(13.dp)).background(aBg).clickable(enabled = enabled, onClick = onClick).padding(vertical = 7.dp, horizontal = 6.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, label, tint = aFg, modifier = Modifier.size(15.dp))
        Spacer(Modifier.width(4.dp))
        Text(label, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.ExtraBold, color = aFg, maxLines = 1)
    }
}

@Composable
private fun IconCircle(icon: ImageVector, desc: String, enabled: Boolean, bg: Color, fg: Color, onClick: () -> Unit) {
    Surface(onClick = onClick, enabled = enabled, shape = CircleShape, color = if (enabled) bg else MaterialTheme.colorScheme.surfaceContainer, modifier = Modifier.size(33.dp)) {
        Box(contentAlignment = Alignment.Center) {
            Icon(icon, desc, tint = if (enabled) fg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f), modifier = Modifier.size(16.dp))
        }
    }
}

fun statusPrimaryColor(st: AttendanceStatus): Color = when (st) {
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    AttendanceStatus.LeftClass -> StatusColors.LeftClass
    else -> StatusColors.Present
}

fun statusOnColor(st: AttendanceStatus): Color = when (st) {
    AttendanceStatus.ABSENT -> StatusColors.OnAbsent
    AttendanceStatus.LATE -> StatusColors.OnLate
    AttendanceStatus.EXCUSED -> StatusColors.OnExcused
    AttendanceStatus.LeftClass -> StatusColors.OnLeftClass
    else -> StatusColors.OnPresent
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) { for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c) }
}
