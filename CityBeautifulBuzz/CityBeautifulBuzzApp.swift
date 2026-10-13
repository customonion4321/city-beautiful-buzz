//
//  CityBeautifulBuzzApp.swift
//  CityBeautifulBuzz
//
//  Application entry point for macOS.
//

import SwiftUI

@main
struct CityBeautifulBuzzApp: App {
    init() {
        NotificationService.shared.requestAuthorization()
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
            HStack(spacing: 3) {
                Image(systemName: "hand.raised.fill")
                Text("CBB")
                    .font(.system(size: 10, weight: .black, design: .monospaced))
            }
        }
        .menuBarExtraStyle(.window)
    }
}
