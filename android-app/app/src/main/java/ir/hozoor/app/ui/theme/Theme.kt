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
    val Present = Color(0xFF1B8A5A)
    val PresentContainer = Color(0xFFD7F5E6)
    val Absent = Color(0xFFD93848)
    val AbsentContainer = Color(0xFFFFDADF)
    val Late = Color(0xFFC87A00)
    val LateContainer = Color(0xFFFFECC7)
    val Excused = Color(0xFF3367D6)
    val ExcusedContainer = Color(0xFFDCE7FF)
    val Unmarked = Color(0xFF757982)
}

private val ExpressiveDarkFallback = darkColorScheme(
    primary = Color(0xFF8CD3FF),
    onPrimary = Color(0xFF00344C),
    primaryContainer = Color(0xFF004C6D),
    secondary = Color(0xFFB5CCDD),
    tertiary = Color(0xFFD9BDFE),
    background = Color(0xFF101418),
    surface = Color(0xFF101418),
    surfaceContainerHigh = Color(0xFF1E252B)
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun HozoorExpressiveTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    reduceMotion: Boolean = false,
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> ExpressiveDarkFallback
        else -> expressiveLightColorScheme()
    }
    val motionScheme = if (reduceMotion) MotionScheme.standard() else MotionScheme.expressive()

    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        MaterialExpressiveTheme(
            colorScheme = colorScheme,
            motionScheme = motionScheme,
            typography = HozoorTypography,
            content = content
        )
    }
}
