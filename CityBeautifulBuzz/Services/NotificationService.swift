//
//  NotificationService.swift
//  CityBeautifulBuzz
//
//  Handles local macOS UserNotifications for critical civic alerts
//  (e.g., water supply cuts, traffic diversions, weather alerts, emergency civic notices).
//

import Foundation
import UserNotifications
import AppKit

@MainActor
public final class NotificationService: NSObject, UNUserNotificationCenterDelegate {
    public static let shared = NotificationService()

    private let notifiedKeysKey = "chd_notified_item_ids_v1"

    private override init() {
        super.init()
        UNUserNotificationCenter.current().delegate = self
    }

    /// Request notification authorization on app startup
    public func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("✅ [NotificationService] macOS notification permission granted.")
            } else if let error = error {
                print("⚠️ [NotificationService] Notification permission error: \(error.localizedDescription)")
            }
        }
    }

    /// Inspect items and post notifications for any new, critical civic alert
    public func checkAndNotify(for items: [NewsItem]) {
        var notifiedIds = Set(UserDefaults.standard.stringArray(forKey: notifiedKeysKey) ?? [])
        let alerts = items.filter { $0.categoryId == "alerts" || $0.importance == "high" }

        for item in alerts.prefix(3) {
            guard !notifiedIds.contains(item.id) else { continue }

            let content = UNMutableNotificationContent()
            content.title = "✋ \(item.sectorTag) • Civic Alert"
            content.subtitle = item.categoryLabel(for: .english)
            content.body = item.title
            content.sound = .default
            content.userInfo = ["article_id": item.id]

            let request = UNNotificationRequest(
                identifier: item.id,
                content: content,
                trigger: nil // Deliver immediately
            )

            UNUserNotificationCenter.current().add(request) { error in
                if let error = error {
                    print("⚠️ [NotificationService] Could not schedule alert: \(error.localizedDescription)")
                } else {
                    print("🔔 [NotificationService] Delivered civic alert banner: \(item.title)")
                }
            }

            notifiedIds.insert(item.id)
        }

        UserDefaults.standard.set(Array(notifiedIds), forKey: notifiedKeysKey)
    }

    // Show banner even when app is active in foreground
    public nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }

    // Deep link into article when user clicks notification
    public nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        if let articleId = response.notification.request.content.userInfo["article_id"] as? String,
           let url = URL(string: "citybuzz://news/\(articleId)") {
            DispatchQueue.main.async {
                NSWorkspace.shared.open(url)
            }
        }
        completionHandler()
    }
}
