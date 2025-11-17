/**
 * Language Detection Agent
 * Detects language (English, Kiswahili, Mixed) using byLLM
 */

walker language_detection_agent {
    has feedback_id;
    has text;
    has detected_language;
    
    can detect_language_with_llm;
    
    root {
        // Use byLLM for language detection
        detected_language = detect_language_with_llm(text);
        
        spawn here --> node::language_result(detected_language);
    }
    
    with language_result {
        // Update database with detected language
        update_feedback_language(feedback_id, here.detected_language);
    }
}

node language_result {
    has language;  // en, sw, mixed
    has confidence;
}

