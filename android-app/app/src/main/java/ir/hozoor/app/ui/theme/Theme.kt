package ir.hozoor.app.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.MaterialExpressiveTheme
import androidx.compose.material3.MotionScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.expressiveLightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection

object StatusColors {
    val Present = Color(0xFF16A34A)
    val OnPresent = Color.White
    val Absent = Color(0xFFDC2626)
    val OnAbsent = Color.White
    val Late = Color(0xFFF59E0B)
    val OnLate = Color(0xFF1A1A1A)
    val Excused = Color(0xFF2563EB)
    val OnExcused = Color.White
    val LeftClass = Color(0xFF9333EA)
    val OnLeftClass = Color.White
}

private val ExpressiveDarkFallback = darkColorScheme(
    primary = Color(0xFF4ADE80), onPrimary = Color(0xFF00391A),
    primaryContainer = Color(0xFF0F5132), onPrimaryContainer = Color(0xFFC2F7D4),
    secondary = Color(0xFF93C5FD), onSecondary = Color(0xFF003063),
    secondaryContainer = Color(0xFF1E3A5F), onSecondaryContainer = Color(0xFFD6E7FF),
    tertiary = Color(0xFFD8B4FE), onTertiary = Color(0xFF3B0764),
    tertiaryContainer = Color(0xFF4C1D95), onTertiaryContainer = Color(0xFFF3E8FF),
    background = Color(0xFF0E1311), surface = Color(0xFF0E1311),
    surfaceContainerLow = Color(0xFF161D1A), surfaceContainer = Color(0xFF1C2521), surfaceContainerHigh = Color(0xFF232E29)
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun HozoorExpressiveTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    reduceMotion: Boolean = false,
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> ExpressiveDarkFallback
        else -> expressiveLightColorScheme()
    }
    val motionScheme = if (reduceMotion) MotionScheme.standard() else MotionScheme.expressive()
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        MaterialExpressiveTheme(colorScheme = colorScheme, motionScheme = motionScheme, typography = HozoorTypography, content = content)
    }
}
