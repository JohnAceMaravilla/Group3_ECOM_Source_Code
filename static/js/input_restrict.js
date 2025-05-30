// USER's INPUT RESTRICTION

// Letters Only 
function letters_only(input) {
    const regex = /^[a-zA-Z\s]*$/;
    
    if (!regex.test(input.value)) {
        input.value = input.value.replace(/[^a-zA-Z\s]/g, '');
    }
}

// Numbers Only 
function numbers_only(input) {
    const regex = /^[0-9]*$/;
    
    if (!regex.test(input.value)) {
        input.value = input.value.replace(/[^0-9]/g, '');
    }
}

// Numbers Only & 11 Digits 
function numbers_only_limit11(input) {
    const regex = /^[0-9]*$/;

    if (!regex.test(input.value)) {
        input.value = input.value.replace(/[^0-9]/g, '');
    }

    if (input.value.length > 11) {
        input.value = input.value.slice(0, 11);
    }
}

// Numbers Only & 4 Digits
function numbers_only_limit4(input) {
    const regex = /^[0-9]*$/;

    if (!regex.test(input.value)) {
        input.value = input.value.replace(/[^0-9]/g, '');
    }

    if (input.value.length > 4) {
        input.value = input.value.slice(0, 4);
    }
}

// Numbers Only & 4 Digits
function numbers_only_limit6(input) {
    const regex = /^[0-9]*$/;

    if (!regex.test(input.value)) {
        input.value = input.value.replace(/[^0-9]/g, '');
    }

    if (input.value.length > 6) {
        input.value = input.value.slice(0, 6);
    }
}


// Numbers, Letters & - Only
function letters_numbers_hyphen(input) {
    const regex = /^[a-zA-Z0-9-]*$/;

    if (!regex.test(input.value)) {
        input.value = input.value.replace(/[^a-zA-Z0-9-]/g, '');
    }
}
