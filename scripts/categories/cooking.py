import random
from datetime import datetime
from logger import get_logger
logger = get_logger("cooking")

RECIPE_DATABASE = [
    {
        "dish": "Butter Chicken",
        "cuisine": "Indian",
        "lines": [
            "Marinate chicken pieces in yogurt, turmeric, chili powder, and garam masala for at least one hour.",
            "Sear the marinated chicken in a hot pan with oil until golden brown on all sides.",
            "In a separate pan, sauté onions, garlic, and ginger until fragrant, then add tomato puree.",
            "Add cream, butter, and a pinch of sugar to the tomato base — stir until smooth and rich.",
            "Combine the chicken with the sauce, simmer for 15 minutes, and garnish with fresh cilantro.",
            "Serve hot with basmati rice or warm naan bread for the perfect comfort meal.",
        ],
    },
    {
        "dish": "Classic Margherita Pizza",
        "cuisine": "Italian",
        "lines": [
            "Prepare the dough: mix flour, yeast, salt, water, and olive oil — knead for 10 minutes and let rise for one hour.",
            "Preheat your oven to the highest setting — ideally 475°F or 250°C with a pizza stone.",
            "Spread San Marzano tomato sauce evenly over the stretched dough, leaving a half-inch border.",
            "Tear fresh mozzarella into pieces and distribute evenly over the sauce.",
            "Bake for 10 to 12 minutes until the crust is golden and the cheese is bubbly.",
            "Finish with fresh basil leaves and a drizzle of extra virgin olive oil before serving.",
        ],
    },
    {
        "dish": "Chicken Tacos",
        "cuisine": "Mexican",
        "lines": [
            "Season chicken thighs with cumin, chili powder, garlic powder, paprika, salt, and lime juice.",
            "Grill or pan-sear the chicken for 6 minutes per side until charred and cooked through.",
            "Let the chicken rest for 5 minutes, then slice into thin strips.",
            "Warm corn tortillas in a dry skillet for 30 seconds each side until pliable.",
            "Assemble tacos with chicken, diced onion, fresh cilantro, and a squeeze of lime.",
            "Top with your favorite salsa, pickled jalapeños, or a drizzle of crema for extra flavor.",
        ],
    },
    {
        "dish": "Vegetable Stir-Fry",
        "cuisine": "Asian",
        "lines": [
            "Prepare the sauce: mix soy sauce, sesame oil, rice vinegar, cornstarch, and a touch of honey.",
            "Slice bell peppers, broccoli, snap peas, carrots, and mushrooms into bite-sized pieces.",
            "Heat a wok or large skillet over high heat — add vegetable oil until it shimmers.",
            "Stir-fry garlic and ginger for 30 seconds, then add the vegetables in order of firmness.",
            "Pour the sauce over the vegetables, toss for 2 minutes until everything is coated and glossy.",
            "Serve immediately over steamed jasmine rice or noodles — garnish with sesame seeds and green onions.",
        ],
    },
    {
        "dish": "Classic American Cheeseburger",
        "cuisine": "American",
        "lines": [
            "Mix ground beef with salt, pepper, and a splash of Worcestershire sauce — form into patties slightly larger than your buns.",
            "Heat a cast-iron skillet to smoking hot — cook patties for 3 minutes per side for medium.",
            "Add a slice of cheddar cheese on top during the last minute and cover to melt.",
            "Toast the burger buns in the same skillet with a bit of butter until golden.",
            "Layer lettuce, tomato, onion, pickles, and your sauces on the bottom bun.",
            "Place the cheesy patty on top, crown with the bun, and serve with crispy fries.",
        ],
    },
    {
        "dish": "Pad Thai",
        "cuisine": "Asian",
        "lines": [
            "Soak flat rice noodles in warm water for 30 minutes until pliable but not fully soft.",
            "Make the sauce: combine tamarind paste, fish sauce, palm sugar, and a squeeze of lime.",
            "Stir-fry shrimp or tofu in a hot wok with garlic until just cooked, then push to the side.",
            "Crack an egg into the wok, scramble quickly, then add the drained noodles.",
            "Pour the sauce over the noodles and toss until evenly coated and slightly caramelized.",
            "Plate and top with crushed peanuts, bean sprouts, lime wedges, and fresh cilantro.",
        ],
    },
    {
        "dish": "Palak Paneer",
        "cuisine": "Indian",
        "lines": [
            "Blanch fresh spinach in boiling water for 2 minutes, then plunge into ice water to keep the vibrant green color.",
            "Blend the blanched spinach into a smooth puree and set aside.",
            "Sauté cubed paneer in butter until golden on all sides, then remove from pan.",
            "In the same pan, cook onions, garlic, ginger, green chilies, and add cumin and garam masala.",
            "Add the spinach puree and a splash of cream — simmer for 5 minutes until thick.",
            "Fold in the paneer cubes, season with salt, and serve hot with roti or naan.",
        ],
    },
    {
        "dish": "Pasta Carbonara",
        "cuisine": "Italian",
        "lines": [
            "Cook spaghetti in well-salted boiling water until al dente — reserve one cup of pasta water before draining.",
            "While the pasta cooks, fry diced guanciale or pancetta until crispy and golden.",
            "Whisk together egg yolks, grated Pecorino Romano, and black pepper in a bowl.",
            "Add the hot drained pasta to the pan with the guanciale — remove from heat.",
            "Pour the egg and cheese mixture over the pasta, tossing quickly — the residual heat creates a creamy sauce.",
            "Add pasta water a tablespoon at a time if needed — serve immediately with extra cheese and pepper.",
        ],
    },
    {
        "dish": "Chicken Burrito Bowl",
        "cuisine": "Mexican",
        "lines": [
            "Season chicken breast with cumin, smoked paprika, oregano, garlic powder, salt, and lime zest.",
            "Grill or bake the chicken at 400°F for 20 minutes, then let it rest and dice.",
            "Cook cilantro lime rice: stir fresh lime juice and chopped cilantro into cooked white rice.",
            "Prepare toppings: black beans, corn, diced tomatoes, avocado, shredded cheese, and sour cream.",
            "Layer the rice in a bowl, add chicken and all toppings in a colorful arrangement.",
            "Drizzle with hot sauce or chipotle mayo and finish with a squeeze of fresh lime.",
        ],
    },
    {
        "dish": "Teriyaki Salmon",
        "cuisine": "Asian",
        "lines": [
            "Make teriyaki glaze: simmer soy sauce, mirin, sake, and brown sugar until reduced and sticky.",
            "Pat salmon fillets dry and season with salt and pepper on both sides.",
            "Sear salmon skin-side down in a hot oiled skillet for 4 minutes until the skin is crispy.",
            "Flip and brush generously with teriyaki glaze — cook for another 3 minutes.",
            "Remove from heat and brush with one more coat of glaze for a beautiful shine.",
            "Serve over steamed rice with steamed broccoli and a sprinkle of sesame seeds.",
        ],
    },
    {
        "dish": "Mac and Cheese",
        "cuisine": "American",
        "lines": [
            "Cook elbow macaroni in salted boiling water until just al dente — drain and set aside.",
            "Make a roux: melt butter in a saucepan, whisk in flour, and cook for one minute.",
            "Slowly pour in warm milk while whisking constantly to create a smooth béchamel sauce.",
            "Add sharp cheddar, mild cheddar, and a pinch of mustard powder — stir until melted and creamy.",
            "Fold in the cooked macaroni, season with salt, pepper, and a dash of paprika.",
            "Transfer to a baking dish, top with breadcrumbs and extra cheese, and broil until golden and bubbly.",
        ],
    },
    {
        "dish": "Falafel Wrap",
        "cuisine": "Middle Eastern",
        "lines": [
            "Soak dried chickpeas overnight — do not use canned, as the texture won't hold together.",
            "Blend chickpeas with fresh parsley, cilantro, garlic, cumin, coriander, and a pinch of baking powder.",
            "Shape the mixture into small patties and fry in hot oil for 3 minutes per side until deep golden.",
            "Warm a large pita or flatbread and spread a generous layer of tahini sauce inside.",
            "Add falafel, diced tomatoes, cucumber, pickled turnips, and shredded lettuce.",
            "Roll tightly, slice in half, and serve with extra tahini and a side of hummus.",
        ],
    },
]


def generate_cooking_content() -> dict:
    recipe = random.choice(RECIPE_DATABASE)
    dish = recipe["dish"]
    cuisine = recipe["cuisine"]

    script_lines = [
        f"Recipe of the Day: {dish} — a delicious {cuisine} dish you can make at home.",
    ] + recipe["lines"] + [
        f"That's your {cuisine}-style {dish}. Enjoy your meal!",
    ]

    title = f"Recipe of the Day: {dish}"

    description = (
        f"🍳 Recipe of the Day | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{title} — {cuisine} Cuisine\n\n"
        f"Easy step-by-step instructions to make this delicious dish at home!\n\n"
        f"#Cooking #Recipe #Food #Meal #Kitchen #HomeCooking"
    )
    tags = ["cooking", "recipe", "food", "meal", "kitchen", "homecooking"]

    return {
        "category": "cooking",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "-2%",
    }