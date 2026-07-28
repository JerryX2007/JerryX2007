# Manual upload

This version follows the guide's SVG approach. Do not convert any asset to GIF.

## Upload the profile

1. Open <https://github.com/JerryX2007/JerryX2007>.
2. Choose **Add file → Upload files**.
3. Upload these four files to the repository root:
   - `README.md`
   - `jerry-ascii.svg`
   - `wordmark.svg`
   - `contrib-heatmap.svg`
4. Commit the files to the `main` branch.
5. Hard-refresh your profile page. The portrait prints once and holds, the `whoami Jerry Xing` line types once and holds, the cursor blinks, the JRX wordmark rocks continuously, and the contribution cells reveal in sequence.

GitHub may cache a previous SVG briefly. If an animation has already completed in your tab, reload the page in a new private window to see its opening sequence again.

## Keep the contribution graph current

This optional step adds the same kind of daily refresh used by the guide.

1. In the repository, choose **Add file → Create new file**.
2. Enter `.github/workflows/update-contribution-graph.yml` as the filename.
3. Copy in the matching workflow file from this package and commit it.
4. Create `scripts/generate_streak_svg.py` the same way and copy in the matching script.
5. Open the repository's **Actions** tab, select **Update contribution graph**, and choose **Run workflow**.

If the workflow cannot push its update, open **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**, and run it again.

## Expected files

```text
JerryX2007/
├── .github/
│   └── workflows/
│       └── update-contribution-graph.yml
├── scripts/
│   └── generate_streak_svg.py
├── README.md
├── contrib-heatmap.svg
├── jerry-ascii.svg
└── wordmark.svg
```
