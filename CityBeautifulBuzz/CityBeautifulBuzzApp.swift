//
//  CityBeautifulBuzzApp.swift
//  CityBeautifulBuzz
//
//  Application entry point for macOS.
//

import SwiftUI
import AppKit

@main
struct CityBeautifulBuzzApp: App {
    init() {
        NotificationService.shared.requestAuthorization()

        // Set the custom Open Hand application icon directly on the Dock server
        if let iconImage = NSImage(named: "AppIcon") ?? (Bundle.main.path(forResource: "AppIcon", ofType: "icns").flatMap { NSImage(contentsOfFile: $0) }) {
            NSApplication.shared.applicationIconImage = iconImage
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified)
        .defaultSize(width: 960, height: 680)

        MenuBarExtra {
            MenuBarView()
        } label: {
            Image(systemName: "hand.raised.fill")
        }
        .menuBarExtraStyle(.window)
    }
}
