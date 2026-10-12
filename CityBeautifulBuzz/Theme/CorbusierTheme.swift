//
//  CorbusierTheme.swift
//  CityBeautifulBuzz
//
//  Design tokens inspired by Le Corbusier's Salubra architectural polychromy
//  and Chandigarh's modernist civic identity.
//

import SwiftUI

public enum CorbusierTheme {
    // ── Signature Polychromy Colors ──────────────────────────────────────────
    /// Burnt terracotta / Brick red (High Court tapestries, sector brickwork)
    public static let terracotta = Color(red: 230/255, green: 110/255, blue: 45/255)

    /// Leisure Valley sage & olive (Rose Garden, urban forest green)
    public static let leisureOlive = Color(red: 126/255, green: 153/255, blue: 84/255)

    /// Capitol periwinkle / violet (Modernist murals, Panjab University)
    public static let capitolViolet = Color(red: 142/255, green: 110/255, blue: 245/255)

    /// Sukhna Lake cobalt blue (Assembly pool reflections, High Court arches)
    public static let sukhnaCobalt = Color(red: 41/255, green: 128/255, blue: 185/255)

    /// Modernist Ochre / Marigold (Sunflower roundabouts)
    public static let sunOchre = Color(red: 240/255, green: 160/255, blue: 35/255)

    /// Civic Alert Vermilion (Urgent warnings, diversions)
    public static let alertVermilion = Color(red: 225/255, green: 65/255, blue: 50/255)

    // ── Neutral Architectural Backgrounds ─────────────────────────────────────
    /// Béton Sand (Warm limestone off-white for light mode canvas)
    public static let betonSand = Color(red: 245/255, green: 242/255, blue: 235/255)

    /// Raw Concrete Slate (Deep tactile charcoal for dark mode canvas)
    public static let rawConcrete = Color(red: 28/255, green: 29/255, blue: 32/255)

    /// Card background in dark mode (Frosted tinted slate)
    public static let darkCardSurface = Color(red: 38/255, green: 40/255, blue: 44/255)

    // ── Geometry Tokens ───────────────────────────────────────────────────────
    public static let cardCornerRadius: CGFloat = 24.0
    public static let badgeCornerRadius: CGFloat = 8.0

    // ── Category Color Mapping ────────────────────────────────────────────────
    public static func color(for categoryId: String) -> Color {
        switch categoryId.lowercased() {
        case "infrastructure":
            return terracotta
        case "events":
            return leisureOlive
        case "education":
            return capitolViolet
        case "governance":
            return sukhnaCobalt
        case "alerts", "safety":
            return alertVermilion
        case "lifestyle", "sports":
            return sunOchre
        case "important_dates":
            return capitolViolet
        default:
            return terracotta
        }
    }
}
