# Upload the Blender scene

The user supplied `Taj_Mahal_Sunset_Conversation.blend` in ChatGPT, but its **binary contents are not yet committed** to this repository because the available GitHub connector supports text-based writes only.

Expected local file:
- Name: `Taj_Mahal_Sunset_Conversation.blend`
- Size: **39,480,987 bytes** (approximately 37.7 MiB)
- SHA-256: `5d10278752f1b8e49dd802e714523d3db84e7502dbb0e194ec4391f2fe4bcac1`
- Destination: `blender/Taj_Mahal_Sunset_Conversation.blend`

## Upload from your computer (Git)

Download the file from the ChatGPT attachment, then open a terminal in its download folder:

```bash
git clone https://github.com/sarfiaroui-oss/blender-video.git
cd blender-video
# Copy the downloaded .blend file into blender/:
# Windows PowerShell: Copy-Item "$HOME/Downloads/Taj_Mahal_Sunset_Conversation.blend" "blender/"
# macOS/Linux: cp ~/Downloads/Taj_Mahal_Sunset_Conversation.blend blender/
git add blender/Taj_Mahal_Sunset_Conversation.blend
git commit -m "Add Taj Mahal sunset Blender scene"
git push origin main
```

This file is below GitHub's 100 MiB regular Git file limit but above the web browser upload limit, so use Git/GitHub Desktop instead of GitHub's website file uploader.

After upload, verify the repository has `blender/Taj_Mahal_Sunset_Conversation.blend`; optionally verify the SHA-256 digest locally.

**Note:** The scene has not yet been opened or rendered in Blender, so asset completeness and animation state are unverified.
