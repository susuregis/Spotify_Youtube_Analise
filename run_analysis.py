"""
Spotify & YouTube Data Analysis Runner
This script provides a command-line interface for running the Spotify & YouTube analysis.
"""

import os
import sys
from spotify_youtube_analysis import SpotifyYouTubeAnalyzer

def print_header():
    print("""
╔═══════════════════════════════════════════════════╗
║ Spotify & YouTube Data Analysis and Visualization ║
╚═══════════════════════════════════════════════════╝
    """)

def print_menu():
    print("\nOPERATIONS:")
    print("1. Extract data from Spotify and YouTube")
    print("2. Analyze Spotify playlists and popular tracks")
    print("3. Analyze YouTube popular video trends")
    print("4. Find correlations between Spotify and YouTube")
    print("5. Analyze regional engagement")
    print("6. Create visualizations")
    print("7. Run full analysis pipeline")
    print("8. Launch interactive dashboard")
    print("0. Exit")
    return input("\nSelect an option (0-8): ")

def main():
    print_header()
    
    analyzer = SpotifyYouTubeAnalyzer()
    
    while True:
        choice = print_menu()
        
        if choice == "1":
            print("\nExtracting data from both platforms...")
            spotify_data = analyzer.extract_spotify_data()
            youtube_data = analyzer.extract_youtube_data()
            print("Data extraction complete.")
            
        elif choice == "2":
            print("\nAnalyzing Spotify playlists and tracks...")
            if analyzer.spotify_tracks_df is None:
                print("No Spotify data available. Please extract data first (option 1).")
            else:
                results = analyzer.analyze_spotify_trends()
                
                print("\n----- SPOTIFY ANALYSIS RESULTS -----")
                if results:
                    print(f"Top artists analyzed: {len(results.get('top_artists_by_count', []))}")
                    print(f"Average track popularity: {results.get('avg_track_popularity', 0):.2f}/100")
                    if 'avg_duration_min' in results:
                        print(f"Average track duration: {results['avg_duration_min']:.2f} minutes")
                    
                    # Display top artists
                    if 'top_artists_by_count' in results:
                        print("\nTop Artists by Track Count:")
                        for i, (_, row) in enumerate(results['top_artists_by_count'].iterrows(), 1):
                            if i <= 5:  # Show top 5
                                print(f"{i}. {row['artist']} - {row['track_count']} tracks")
        
        elif choice == "3":
            print("\nAnalyzing YouTube popular video trends...")
            if analyzer.youtube_videos_df is None:
                print("No YouTube data available. Please extract data first (option 1).")
            else:
                results = analyzer.analyze_youtube_trends()
                
                print("\n----- YOUTUBE ANALYSIS RESULTS -----")
                if results:
                    print(f"Average views: {results.get('avg_view_count', 0):.0f}")
                    print(f"Average likes: {results.get('avg_like_count', 0):.0f}")
                    print(f"Average comments: {results.get('avg_comment_count', 0):.0f}")
                    print(f"Average engagement rate: {results.get('avg_engagement_rate', 0):.4f}")
                    
                    # Display top categories
                    if 'top_categories_by_count' in results:
                        print("\nTop Video Categories:")
                        for i, (_, row) in enumerate(results['top_categories_by_count'].iterrows(), 1):
                            if i <= 5:  # Show top 5
                                print(f"{i}. {row['category']} - {row['count']} videos")
        
        elif choice == "4":
            print("\nCorrelating Spotify and YouTube data...")
            if analyzer.spotify_tracks_df is None or analyzer.youtube_videos_df is None:
                print("Both Spotify and YouTube data are required. Please extract data first (option 1).")
            else:
                correlations, correlation_df = analyzer.correlate_spotify_youtube()
                
                print("\n----- CORRELATION RESULTS -----")
                if correlations:
                    print(f"Music video matches found: {correlations.get('music_video_matches', 0)}")
                    if 'popularity_vs_views_corr' in correlations:
                        corr = correlations['popularity_vs_views_corr']
                        print(f"Spotify popularity vs YouTube views correlation: {corr:.4f}")
                        
                        # Interpretation
                        if abs(corr) < 0.2:
                            print("Interpretation: Very weak correlation")
                        elif abs(corr) < 0.4:
                            print("Interpretation: Weak correlation")
                        elif abs(corr) < 0.6:
                            print("Interpretation: Moderate correlation")
                        elif abs(corr) < 0.8:
                            print("Interpretation: Strong correlation")
                        else:
                            print("Interpretation: Very strong correlation")
        
        elif choice == "5":
            print("\nAnalyzing regional engagement...")
            
            # Ask for regions to analyze
            regions_input = input("Enter region codes to analyze (comma-separated, e.g., BR,US,GB): ")
            if regions_input:
                regions = [r.strip() for r in regions_input.split(",")]
            else:
                regions = ['BR', 'US', 'GB', 'JP', 'IN']
                
            regional_df = analyzer.analyze_regional_engagement(regions)
            
            print("\n----- REGIONAL ANALYSIS RESULTS -----")
            if regional_df is not None and not regional_df.empty:
                print(f"Regions analyzed: {len(regional_df)}")
                print("\nEngagement metrics by region:")
                for i, (_, row) in enumerate(regional_df.iterrows()):
                    print(f"\nRegion: {row['region']}")
                    print(f"  Average views: {row['avg_views']:.0f}")
                    print(f"  Average engagement rate: {row['avg_engagement']:.4f}")
                    if 'top_category' in row:
                        print(f"  Top category: {row['top_category']}")
        
        elif choice == "6":
            print("\nCreating visualizations...")
            if analyzer.spotify_tracks_df is None or analyzer.youtube_videos_df is None:
                print("Both Spotify and YouTube data are required. Please extract data first (option 1).")
            else:
                analyzer.create_visualizations()
                print(f"\nVisualizations created successfully in 'visualizations' directory.")
        
        elif choice == "7":
            print("\nRunning full analysis pipeline...")
            results = analyzer.run()
            print("\nFull analysis complete!")
        
        elif choice == "8":
            print("\nLaunching interactive dashboard...")
            analyzer.create_dashboard()
            print("\nTo view the dashboard, run: python spotify_youtube_analysis.py runserver")
        
        elif choice == "0":
            print("\nExiting program. Goodbye!")
            break
        
        else:
            print("\nInvalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
