//
//  AppLanguage.swift
//  CityBeautifulBuzz
//
//  Manages English ⇄ Hindi bilingual toggle state.
//

import SwiftUI

public enum AppLanguage: String, CaseIterable, Identifiable, Codable, Sendable {
    case english = "en"
    case hindi = "hi"

    public var id: String { rawValue }

    public var title: String {
        switch self {
        case .english: return "English"
        case .hindi: return "हिंदी"
        }
    }

    public var shortLabel: String {
        switch self {
        case .english: return "EN"
        case .hindi: return "हिं"
        }
    }

    public var flagIcon: String {
        switch self {
        case .english: return "🇬🇧"
        case .hindi: return "🇮🇳"
        }
    }
}
