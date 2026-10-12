//
//  CityBeautifulBuzzApp.swift
//  CityBeautifulBuzz
//
//  Application entry point for macOS.
//

import SwiftUI

@main
struct CityBeautifulBuzzApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified)
        .defaultSize(width: 960, height: 680)
    }
}
