import React from 'react';
import Balatro from './Balatro';
import SpotlightCard from './SpotlightCard';
import { Globe, Check } from 'lucide-react';
import './LanguageSelection.css';

const LanguageSelection = ({ onLanguageSelect, selectedLanguage }) => {
    const languages = [
        {
            code: 'english',
            name: 'English',
            nativeName: 'English',
            flag: '🇬🇧',
            spotlightColor: 'rgba(59, 130, 246, 0.3)'
        },
        {
            code: 'tamil',
            name: 'Tamil',
            nativeName: 'தமிழ்',
            flag: '🇮🇳',
            spotlightColor: 'rgba(239, 68, 68, 0.3)'
        },
        {
            code: 'hindi',
            name: 'Hindi',
            nativeName: 'हिन्दी',
            flag: '🇮🇳',
            spotlightColor: 'rgba(249, 115, 22, 0.3)'
        },
        {
            code: 'telugu',
            name: 'Telugu',
            nativeName: 'తెలుగు',
            flag: '🇮🇳',
            spotlightColor: 'rgba(168, 85, 247, 0.3)'
        },
        {
            code: 'kannada',
            name: 'Kannada',
            nativeName: 'ಕನ್ನಡ',
            flag: '🇮🇳',
            spotlightColor: 'rgba(34, 197, 94, 0.3)'
        }
    ];

    return (
        <div className="language-selection-container">
            <Balatro
                isRotate={false}
                mouseInteraction={true}
                pixelFilter={700}
                color1="#667eea"
                color2="#764ba2"
                color3="#0a0a0a"
            />

            <div className="language-selection-content">
                <div className="language-header">
                    <div className="language-icon">
                        <Globe size={48} />
                    </div>
                    <h1 className="language-title">Choose Your Interview Language</h1>
                    <p className="language-subtitle">
                        Select the language you're most comfortable with for the interview
                    </p>
                </div>

                <div className="language-grid">
                    {languages.map((language) => (
                        <SpotlightCard
                            key={language.code}
                            className={`language-card ${selectedLanguage === language.code ? 'selected' : ''}`}
                            spotlightColor={language.spotlightColor}
                            onClick={() => onLanguageSelect(language.code)}
                        >
                            <div className="language-card-content">
                                <div className="language-flag">{language.flag}</div>
                                <div className="language-info">
                                    <h3 className="language-name">{language.name}</h3>
                                    <p className="language-native">{language.nativeName}</p>
                                </div>
                                {selectedLanguage === language.code && (
                                    <div className="language-check">
                                        <Check size={24} />
                                    </div>
                                )}
                            </div>
                        </SpotlightCard>
                    ))}
                </div>

                <div className="language-footer">
                    <p className="language-note">
                        💡 You can speak and answer questions in your selected language
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LanguageSelection;
