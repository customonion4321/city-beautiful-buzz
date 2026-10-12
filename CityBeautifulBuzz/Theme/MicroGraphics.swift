//
//  MicroGraphics.swift
//  CityBeautifulBuzz
//
//  Parametric micro-visualizations directly inspired by the user's reference designs:
//  1. WaveformRhythmView (Histogram wave bars - orange card style)
//  2. SegmentedRingView  (Circular segmented gauge - green card style)
//  3. DotMatrixView      (Modernist dot grid - purple card style)
//

import SwiftUI

// ── 1. Waveform Rhythm View (Histogram Bars) ──────────────────────────────────
public struct WaveformRhythmView: View {
    let heights: [CGFloat] = [0.25, 0.4, 0.65, 0.5, 0.85, 1.0, 0.75, 0.55, 0.45, 0.35, 0.2]

    public init() {}

    public var body: some View {
        HStack(alignment: .bottom, spacing: 3.5) {
            ForEach(0..<heights.count, id: \.self) { index in
                Capsule()
                    .fill(Color.white.opacity(0.85))
                    .frame(width: 4.5, height: max(6, 38 * heights[index]))
            }
        }
        .frame(height: 40)
    }
}

// ── 2. Segmented Ring View (Circular Gauge) ───────────────────────────────────
public struct SegmentedRingView: View {
    public let scoreText: String
    public let sublabel: String

    public init(scoreText: String = "TOP", sublabel: String = "VERIFIED") {
        self.scoreText = scoreText
        self.sublabel = sublabel
    }

    public var body: some View {
        ZStack {
            // Segmented circular arc
            Circle()
                .stroke(
                    Color.white.opacity(0.3),
                    style: StrokeStyle(lineWidth: 4.5, lineCap: .round, dash: [14, 5])
                )
                .frame(width: 46, height: 46)

            Circle()
                .trim(from: 0.1, to: 0.85)
                .stroke(
                    Color.white.opacity(0.95),
                    style: StrokeStyle(lineWidth: 4.5, lineCap: .round, dash: [14, 5])
                )
                .frame(width: 46, height: 46)
                .rotationEffect(.degrees(-90))

            VStack(spacing: 0) {
                Text(scoreText)
                    .font(.system(size: 11, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Text(sublabel)
                    .font(.system(size: 7, weight: .semibold, design: .monospaced))
                    .foregroundColor(Color.white.opacity(0.8))
            }
        }
        .frame(width: 50, height: 50)
    }
}

// ── 3. Dot Matrix Grid View (Pill Dots) ────────────────────────────────────────
public struct DotMatrixView: View {
    private let rows = 3
    private let columns = 6

    public init() {}

    public var body: some View {
        VStack(spacing: 3.5) {
            ForEach(0..<rows, id: \.self) { row in
                HStack(spacing: 3.5) {
                    ForEach(0..<columns, id: \.self) { col in
                        let isLit = (row == 1 && col >= 2 && col <= 4) || (row == 0 && col == 3) || (row == 2 && col == 3)
                        Circle()
                            .fill(isLit ? Color.white : Color.white.opacity(0.28))
                            .frame(width: 5.5, height: 5.5)
                    }
                }
            }
        }
        .frame(height: 36)
    }
}

// ── Selector to pick micro-graphic based on category ──────────────────────────
public struct CategoryMicroGraphicView: View {
    public let categoryId: String

    public init(categoryId: String) {
        self.categoryId = categoryId
    }

    public var body: some View {
        switch categoryId.lowercased() {
        case "infrastructure", "alerts", "governance":
            WaveformRhythmView()
        case "events", "lifestyle", "sports":
            SegmentedRingView(scoreText: "CHD", sublabel: "BUZZ")
        default:
            DotMatrixView()
        }
    }
}
