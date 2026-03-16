function run() {
    try {
        const input = document.getElementById('input').value.trim();
        const outputElement = document.getElementById('output');
        let parsedInput;
        
        // Parse input JSON
        try {
            parsedInput = JSON.parse(input);
        } catch (e) {
            throw new Error('Invalid JSON input');
        }
        
        // Validate input structure
        if (!validateInput(parsedInput)) {
            throw new Error('Invalid input structure');
        }
        
        // Process input
        const experience = createExperience(parsedInput);
        
        // Output processed experience
        outputElement.textContent = JSON.stringify(experience, null, 2);
        
    } catch (e) {
        document.getElementById('output').textContent = `Error: ${e.message}`;
    }
}

function validateInput(data) {
    return typeof data.experience === 'string' &&
           data.experience.length <= 280 &&
           Array.isArray(data.pros) &&
           Array.isArray(data.cons) &&
           typeof data.rating === 'number' &&
           data.rating >= 1 &&
           data.rating <= 5;
}

function createExperience(input) {
    const prosSummary = summarizeTags(input.pros);
    const consSummary = summarizeTags(input.cons);
    
    return {
        experience: input.experience,
        pros: input.pros,
        cons: input.cons,
        rating: input.rating,
        prosSummary: prosSummary,
        consSummary: consSummary,
        helpfulCount: 0
    };
}

function summarizeTags(tags) {
    const tagCount = tags.reduce((acc, tag) => {
        acc[tag] = (acc[tag] || 0) + 1;
        return acc;
    }, {});
    
    const sortedTags = Object.entries(tagCount)
                             .sort((a, b) => b[1] - a[1])
                             .map(entry => entry[0]);
    
    return sortedTags.slice(0, 3);
}