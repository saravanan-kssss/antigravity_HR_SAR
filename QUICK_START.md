# Quick Start Guide - Language Selection Feature

## ✅ Setup Complete!

All files have been created and the `ogl` package is already installed. You're ready to go!

## 🚀 How to Run

### 1. Start the Backend Server
```bash
cd server
python main.py
```

### 2. Start the Frontend
```bash
cd client
npm run dev
```

### 3. Test the Language Selection

1. Open your browser to `http://localhost:5173` (or the URL shown by Vite)
2. Navigate to the interview page
3. Enter candidate details (if not coming from application)
4. **You'll see the beautiful language selection page!**
5. Click on any language card (English, Tamil, Hindi, Telugu, or Kannada)
6. The card will show a checkmark and auto-proceed to device check
7. The interview will be conducted in your selected language

## 🎨 What You'll See

### Language Selection Page Features:
- **Animated Background**: Beautiful shader-based animation with mouse interaction
- **5 Language Cards**: Each with flag emoji and native script
- **Spotlight Effect**: Cards light up as you hover over them
- **Visual Feedback**: Checkmark appears on selected language
- **Smooth Transition**: Auto-proceeds to device check after 0.5 seconds

### Supported Languages:
- 🇬🇧 **English** - Full support
- 🇮🇳 **Tamil (தமிழ்)** - Full support
- 🇮🇳 **Hindi (हिन्दी)** - Full support
- 🇮🇳 **Telugu (తెలుగు)** - Full support
- 🇮🇳 **Kannada (ಕನ್ನಡ)** - Full support

## 🔧 No Additional Setup Required

**You DO NOT need to:**
- ❌ Install Tailwind CSS
- ❌ Run shadcn CLI
- ❌ Configure tsconfig.json
- ❌ Install any other packages

**Everything is already set up!** The components use vanilla CSS and are ready to use.

## 📝 How It Works

### Interview Flow:
```
1. Enter Details (Name, Email)
   ↓
2. Select Language (NEW PAGE)
   ↓
3. Device Check (Camera, Mic)
   ↓
4. Interview Starts
   ↓
5. Questions in Selected Language
   ↓
6. TTS speaks in Selected Language
   ↓
7. STT listens for Selected Language
```

### Technical Flow:
```javascript
// User selects "Tamil"
setSelectedLanguage('tamil')

// Question generation uses selected language
fetch('/api/interviews/1/questions/generate', {
    body: JSON.stringify({ 
        language: 'tamil'  // ← Dynamic!
    })
})

// TTS uses Tamil voice
text_to_speech(text, language_code='ta-IN')

// STT listens for Tamil
startRecording('tamil')
```

## 🎯 Testing Different Languages

### Test English:
1. Select English on language page
2. Questions will be in English
3. TTS will use English voice (en-US)
4. STT will recognize English speech

### Test Tamil:
1. Select Tamil (தமிழ்) on language page
2. Questions will be in Tamil
3. TTS will use Tamil voice (ta-IN)
4. STT will recognize Tamil speech

### Test Other Languages:
Same process for Hindi, Telugu, and Kannada!

## 🐛 Troubleshooting

### If you see a blank page:
- Check browser console for errors
- Make sure both backend and frontend are running
- Verify `ogl` package is installed: `npm list ogl`

### If background doesn't animate:
- Check if your browser supports WebGL
- Open browser console and look for WebGL errors
- Try a different browser (Chrome/Firefox recommended)

### If language doesn't change:
- Check browser console for API errors
- Verify backend is running on port 8000
- Check Network tab to see if correct language is sent

### If you see "Cannot find module 'ogl'":
```bash
cd client
npm install ogl
```

## 📱 Mobile Support

The language selection page is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

## 🎨 Customization

### Change Background Colors:
Edit `client/src/components/LanguageSelection.jsx`:
```javascript
<Balatro
    color1="#667eea"  // Change this
    color2="#764ba2"  // Change this
    color3="#0a0a0a"  // Change this
/>
```

### Add More Languages:
Edit the `languages` array in `LanguageSelection.jsx`:
```javascript
const languages = [
    // ... existing languages
    {
        code: 'malayalam',
        name: 'Malayalam',
        nativeName: 'മലയാളം',
        flag: '🇮🇳',
        spotlightColor: 'rgba(255, 193, 7, 0.3)'
    }
];
```

### Change Auto-Proceed Delay:
Edit `handleLanguageSelect` in `InterviewPage.jsx`:
```javascript
setTimeout(() => {
    setStage('deviceCheck');
    initializeDevices();
}, 500);  // Change 500 to any milliseconds
```

## 🎉 That's It!

You're all set! The language selection feature is fully integrated and ready to use. Enjoy the multilingual interview experience!

## 📚 Additional Resources

- See `LANGUAGE_SELECTION_SETUP.md` for detailed technical documentation
- Check `client/src/components/LanguageSelection.jsx` for component code
- Review `client/src/InterviewPage.jsx` for integration details
