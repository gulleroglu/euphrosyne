# Place Types (New) - Google Places API Documentation

Use these types with `--category` in `search_places.py`. Types marked with * are newer (Nov 2024).

## Quick Reference for Activities Agent

### Best Types for Occasion Activities

| Need | Best Types | Alternative Query |
|------|------------|-------------------|
| Fine dining | `fine_dining_restaurant`* | `--query "michelin star"` |
| Wine experiences | `wine_bar`* | `--query "winery vineyard tasting"` |
| Cultural sites | `museum`, `historical_landmark`, `cultural_landmark`* | |
| Outdoor activities | `hiking_area`*, `park`, `botanical_garden`* | |
| Entertainment | `casino`, `night_club`, `concert_hall`* | |
| Wellness | `spa`, `wellness_center`*, `sauna`* | |
| Tours | `tour_agency`*, `visitor_center` | `--query "guided tour"` |

### Things WITHOUT a Specific Type (use query)

| Looking For | Use This Query |
|-------------|----------------|
| Champagne houses | `--query "champagne house tasting"` |
| Wineries/vineyards | `--query "winery vineyard"` |
| Châteaux/castles | `--query "chateau castle"` |
| Cooking classes | `--query "cooking class workshop"` |
| Boat tours | `--query "boat tour cruise"` |
| Hot air balloon | `--query "hot air balloon"` |
| Helicopter tours | `--query "helicopter tour"` |
| Bike rentals | `--query "bike rental cycling"` |

### Search Strategy

1. **Specific type available** → Use `--category`:
   ```bash
   --category "fine_dining_restaurant"
   ```

2. **No specific type** → Use `--query`:
   ```bash
   --query "champagne cellar tour"
   ```

3. **Combine for precision**:
   ```bash
   --category "restaurant" --query "gastronomic michelin"
   --category "tourist_attraction" --query "champagne house"
   ```

---

## Overview

"Place types are categories that identify the characteristics of a place. A place can have one or more place types assigned to it."

Place types serve multiple functions:
- Included in responses from Place Details, Nearby Search, Text Search, and Autocomplete requests
- Used as filters to restrict search results to matching places
- Organized across two primary tables (Table A and Table B)

## Primary Types (Table A)

Types in Table A are usable for filtering and can refine Nearby Search and Text Search requests. Many types were added in the November 7, 2024 release (marked with asterisks).

### Automotive
car_dealer, car_rental, car_repair, car_wash, electric_vehicle_charging_station, gas_station, parking, rest_stop

### Business
corporate_office*, farm, ranch*

### Culture
art_gallery, art_studio*, auditorium*, cultural_landmark*, historical_place*, monument*, museum, performing_arts_theater, sculpture*

### Education
library, preschool, primary_school, school, secondary_school, university

### Entertainment and Recreation
adventure_sports_center*, amphitheatre*, amusement_center, amusement_park, aquarium, banquet_hall, barbecue_area*, botanical_garden*, bowling_alley, casino, childrens_camp*, comedy_club*, community_center, concert_hall*, convention_center, cultural_center, cycling_park*, dance_hall*, dog_park, event_venue, ferris_wheel*, garden*, hiking_area*, historical_landmark, internet_cafe*, karaoke*, marina, movie_rental, movie_theater, national_park, night_club, observation_deck*, off_roading_area*, opera_house*, park, philharmonic_hall*, picnic_ground*, planetarium*, plaza*, roller_coaster*, skateboard_park*, state_park*, tourist_attraction, video_arcade*, visitor_center, water_park*, wedding_venue, wildlife_park*, wildlife_refuge*, zoo

### Facilities
public_bath*, public_bathroom*, stable*

### Finance
accounting, atm, bank

### Food and Drink
acai_shop*, afghani_restaurant*, african_restaurant*, american_restaurant, asian_restaurant*, bagel_shop*, bakery, bar, bar_and_grill*, barbecue_restaurant, brazilian_restaurant, breakfast_restaurant, brunch_restaurant, buffet_restaurant*, cafe, cafeteria*, candy_store*, cat_cafe*, chinese_restaurant, chocolate_factory*, chocolate_shop*, coffee_shop, confectionery*, deli*, dessert_restaurant*, dessert_shop*, diner*, dog_cafe*, donut_shop*, fast_food_restaurant, fine_dining_restaurant*, food_court*, french_restaurant, greek_restaurant, hamburger_restaurant, ice_cream_shop, indian_restaurant, indonesian_restaurant, italian_restaurant, japanese_restaurant, juice_shop*, korean_restaurant*, lebanese_restaurant, meal_delivery, meal_takeaway, mediterranean_restaurant, mexican_restaurant, middle_eastern_restaurant, pizza_restaurant, pub*, ramen_restaurant, restaurant, sandwich_shop, seafood_restaurant, spanish_restaurant, steak_house, sushi_restaurant, tea_house*, thai_restaurant, turkish_restaurant, vegan_restaurant, vegetarian_restaurant, vietnamese_restaurant, wine_bar*

### Geographical Areas
administrative_area_level_1, administrative_area_level_2, country, locality, postal_code, school_district

### Government
city_hall, courthouse, embassy, fire_station, government_office*, local_government_office, neighborhood_police_station (Japan only), police, post_office

### Health and Wellness
chiropractor*, dental_clinic, dentist, doctor, drugstore, hospital, massage*, medical_lab*, pharmacy, physiotherapist, sauna*, skin_care_clinic*, spa, tanning_studio*, wellness_center*, yoga_studio*

### Housing
apartment_building*, apartment_complex*, condominium_complex*, housing_complex*

### Lodging
bed_and_breakfast, budget_japanese_inn*, campground, camping_cabin, cottage, extended_stay_hotel, farmstay, guest_house, hostel*, hotel*, inn*, japanese_inn*, lodging, mobile_home_park*, motel, private_guest_room, resort_hotel, rv_park

### Natural Features
beach*

### Places of Worship
church, hindu_temple, mosque, synagogue

### Services
astrologer*, barber_shop, beautician*, beauty_salon, body_art_service*, catering_service*, cemetery, child_care_agency, consultant, courier_service, electrician, florist, food_delivery*, foot_care*, funeral_home, hair_care, hair_salon, insurance_agency, laundry*, lawyer, locksmith, makeup_artist*, moving_company, nail_salon*, painter, plumber, psychic*, real_estate_agency, roofing_contractor, storage, summer_camp_organizer*, tailor, telecommunications_service_provider, tour_agency*, tourist_information_center*, travel_agency, veterinary_care

### Shopping
asian_grocery_store*, auto_parts_store, bicycle_store, book_store, butcher_shop*, cell_phone_store, clothing_store, convenience_store, department_store, discount_store, electronics_store, food_store*, furniture_store, gift_shop, grocery_store, hardware_store, home_goods_store, home_improvement_store, jewelry_store, liquor_store, market, pet_store, shoe_store, shopping_mall, sporting_goods_store, store, supermarket, warehouse_store*, wholesaler

### Sports
arena*, athletic_field, fishing_charter*, fishing_pond*, fitness_center, golf_course, gym, ice_skating_rink*, playground*, ski_resort, sports_activity_location*, sports_club, sports_coaching*, sports_complex, stadium, swimming_pool

### Transportation
airport, airstrip*, bus_station, bus_stop, ferry_terminal, heliport, international_airport*, light_rail_station, park_and_ride*, subway_station, taxi_stand, train_station, transit_depot, transit_station, truck_stop

## Additional Types (Table B)

"Values from Table B may NOT be used as part of a request, except as the values to the includedPrimaryTypes parameter for Autocomplete."

administrative_area_level_3 through 7, archipelago, colloquial_area, continent, establishment, finance, food, general_contractor, geocode, health, intersection, landmark, natural_feature, neighborhood, place_of_worship, plus_code, point_of_interest, political, postal_code_prefix, postal_code_suffix, postal_town, premise, route, street_address, sublocality, sublocality_level_1 through 5, subpremise, town_square

## Address Types and Component Types

Addresses can be tagged with types including: street_address, route, intersection, political, country, administrative_area_level_1 through 7, colloquial_area, locality, sublocality, neighborhood, premise, subpremise, plus_code, postal_code, natural_feature, airport, park, point_of_interest, floor, landmark, parking, post_box, postal_town, room, street_number, bus_station, train_station, and transit_station.
