package ir.hozoor.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import ir.hozoor.app.R

val VazirmatnFontFamily = FontFamily(
    Font(R.font.vazirmatn_regular, FontWeight.Normal),
    Font(R.font.vazirmatn_medium, FontWeight.Medium),
    Font(R.font.vazirmatn_bold, FontWeight.Bold),
    Font(R.font.vazirmatn_extrabold, FontWeight.ExtraBold),
)

private val Base = Typography()

val HozoorTypography = Typography(
    displayLarge = Base.displayLarge.copy(fontFamily = VazirmatnFontFamily),
    displayMedium = Base.displayMedium.copy(fontFamily = VazirmatnFontFamily),
    displaySmall = Base.displaySmall.copy(fontFamily = VazirmatnFontFamily),
    headlineLarge = Base.headlineLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.ExtraBold),
    headlineMedium = Base.headlineMedium.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    headlineSmall = Base.headlineSmall.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleLarge = Base.titleLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleMedium = Base.titleMedium.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleSmall = Base.titleSmall.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Medium),
    bodyLarge = Base.bodyLarge.copy(fontFamily = VazirmatnFontFamily),
    bodyMedium = Base.bodyMedium.copy(fontFamily = VazirmatnFontFamily),
    bodySmall = Base.bodySmall.copy(fontFamily = VazirmatnFontFamily),
    labelLarge = Base.labelLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Medium),
    labelMedium = Base.labelMedium.copy(fontFamily = VazirmatnFontFamily),
    labelSmall = Base.labelSmall.copy(fontFamily = VazirmatnFontFamily),
)
