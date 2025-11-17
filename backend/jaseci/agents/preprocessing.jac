/**
 * Preprocessing Agent
 * Cleans and normalizes text data
 */

walker preprocessing_agent {
    has feedback_id;
    has raw_text;
    has cleaned_text;
    
    can clean_text, normalize, remove_noise;
    
    root {
        cleaned_text = clean_text(raw_text);
        cleaned_text = normalize(cleaned_text);
        cleaned_text = remove_noise(cleaned_text);
        
        spawn here --> node::cleaned_feedback(cleaned_text);
    }
    
    with cleaned_feedback {
        // Update database with cleaned text
        update_feedback(feedback_id, here.cleaned_text);
    }
}

node cleaned_feedback {
    has cleaned_text;
    has original_length;
    has cleaned_length;
}

