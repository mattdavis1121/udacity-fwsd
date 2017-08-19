var Brewery = function (data, viewModel) {
    var self = this;

    // id will be used to ensure breweries stored
    // in memory are unique.
    this.id = ko.observable('brewery_' + data.id);

    // Various desriptors
    this.name = ko.observable(data.brewery.name);
    this.description = ko.observable(data.brewery.description);
    this.established = ko.observable(data.brewery.established);
    this.type = ko.observable(data.locationTypeDisplay);

    // Location data
    this.lat = ko.observable(data.latitude);
    this.lng = ko.observable(data.longitude);
    this.distance = ko.observable(data.distance);
    this.coords = ko.computed(function () {
        return {lat: self.lat(), lng: self.lng()};
    });
    this.directionsLink = ko.computed(function () {
        return "https://www.google.com/maps/dir//" + self.lat() + "," + self.lng() + "/";
    });

    this.phone = ko.observable(data.phone);
    this.locality = ko.observable(data.locality);
    this.region = ko.observable(data.region);
    this.streetAddress = ko.observable(data.streetAddress);
    this.postalCode = ko.observable(data.postalCode);
    this.fullAddress = ko.computed(function () {
        return self.streetAddress() + ', ' + self.locality() + ', ' + self.region() + ' ' + self.postalCode();
    });
    this.website = ko.observable(data.website);

    // Images is an object containing various sizes of
    // logos for the brewery. Common structure is...
    // {icon: url, medium: url, large: url,
    //  squareMedium: url, squareLarge: url}
    // but none of these keys can be assumed to be present
    // as not all breweries have logos.
    this.images = ko.observable(data.brewery.images);

    // Track last-clicked location
    this.isActive = ko.observable(false);

    // Store an unshown marker for each brewery,
    // then just toggle visible/hidden.
    //
    // Rubric says markers can't be obvserables, so this is a plain object
    this.marker = makeMarker(this);
    this.marker.breweryObj = this;

    this.viewModel = viewModel;
};

var ViewModel = function () {
    var self = this;

    // KO vars here
    this.locationsList = ko.observableArray([]);
    this.promptVisible = ko.computed(function () {
        return self.locationsList().length === 0;
    });
    this.addressSearch = ko.observable();
    this.currentLocation = ko.observable();
    this.drawerVisible = ko.observable(false);
    this.locationClickDisabled = ko.observable(false);
    this.typeFilter = ko.observable();
    this.distanceFilter = ko.observable();
    this.distanceOptions = ko.observableArray([20, 10, 5]);
    this.errors = ko.observableArray([]);
    this.errorsVisible = ko.computed(function () {
        return self.errors().length > 0;
    });
    this.promptOrErrorVisible = ko.computed(function () {
        return self.promptVisible() || self.errorsVisible();
    });

    // Computed vals
    this.breweryTypes = ko.computed(function () {
        // Get a list of unique brewery types for filter selections
        var types = [];
        self.locationsList().forEach(function (location) {
            if (!types.includes(location.type())) {
                types.push(location.type());
            }
        });
        return types;
    });
    this.displayBreweries = ko.computed(function () {
        // Handle brewery-type and distance filters
        // If neither filter is set, return locationsList unchanged.
        // If only one of the two is set, apply the appropriate filter and return
        // If both are set, apply both and return
        if (!self.typeFilter() && !self.distanceFilter()) {
            return self.locationsList();
        } else if (self.typeFilter() && !self.distanceFilter()) {
            return ko.utils.arrayFilter(self.locationsList(), function (location) {
                return location.type() == self.typeFilter();
            });
        } else if (!self.typeFilter() && self.distanceFilter()) {
            return ko.utils.arrayFilter(self.locationsList(), function (location) {
                return location.distance() <= self.distanceFilter();
            });
        } else {
            return ko.utils.arrayFilter(self.locationsList(), function (location) {
                return location.type() == self.typeFilter() && location.distance() <= self.distanceFilter();
            });
        }
    });
    this.displayBreweries.subscribe(function (newArray) {
        if (newArray.length > 0) {
            self.locationClick(newArray[0]);
            self.renderMarkers(newArray);
        }
    });

    this.renderMarkers = function (breweriesArray) {
        // Unset all map markers, then render only those in the array passed in
        self.locationsList().forEach(function (brewery) {
            brewery.marker.setMap(null);
        });
        breweriesArray.forEach(function (brewery) {
            brewery.marker.setMap(map);
        });
    };

    this.scrollBreweryIntoView = function (clickedLocation) {
        try {
            var brewery = $('#' + clickedLocation.id());
            var first_brewery = $('.breweries > .brewery');
            var breweries = $('.breweries');
            // Top-to-bottom scroll for desktop view
            breweries.animate({scrollTop: brewery.offset().top - first_brewery.offset().top});
            // Left-to-right scroll for mobile
            breweries.animate({scrollLeft: brewery.offset().left - first_brewery.offset().left});
        }
        catch (err) {
            // Do nothing. This is just to prevent an error when calling
            // the locationClick function on address search.
        }
    };

    this.locationClick = function (clickedLocation) {

        if (!self.locationClickDisabled()) {
            self.locationClickDisabled(true);
            self.scrollBreweryIntoView(clickedLocation);

            // First, reset last-clicked marker to default
            if (self.currentLocation()) {
                self.currentLocation().marker.setIcon('../static/img/dark-green-marker-med.png');
                self.currentLocation().marker.setZIndex();
                self.currentLocation().isActive(false);
            }

            // Then register new currentLocation and use custom marker
            clickedLocation.marker.setIcon('../static/img/light-green-marker-med.png');
            clickedLocation.marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            clickedLocation.isActive(true);
            self.currentLocation(clickedLocation);
            self.locationClickDisabled(false);
        }
    };

    this.toggleDrawer = function (clickedMarker) {
        self.drawerVisible(!self.drawerVisible());
    };

    this.getNearbyBreweries = function (position) {
        // Main data-driver for application. Get breweries within 30 miles of search,
        // then add to self.locationsList(). Timeout set to 3 seconds.
        var data = {
            lat: position.lat(),
            lng: position.lng(),
            radius: 30,
            key: '57c867fabb0e35e3540fe6119f029846',
            endpoint: '/search/geo/point'
        };

        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/proxy",
            data: JSON.stringify(data),
            success: function (breweryJSON) {
                self.errors([]);    //Unset all errors on sucess
                console.log(breweryJSON);
                var breweries = [];
                breweryJSON.data.forEach(function (breweryData) {
                    var brewery = new Brewery(breweryData, self);
                    breweries.push(brewery);
                });
                self.locationsList(breweries);
            },
            timeout: 3000,
            error: function (jqXHR, textStatus, errorThrown) {
                self.errors.push('Connection to BreweryDB temporarily unavailable');
            }
        });
    };

    this.resetLocationsList = function () {
        // Remove all current markers from map, reset map bounds, and empty observableArray
        self.locationsList().forEach(function (location) {
            location.marker.setMap(null);
        });
        mapBounds = new google.maps.LatLngBounds();
        self.locationsList([]);
    };

    this.searchLocation = function () {
        self.drawerVisible(false);
        self.resetLocationsList();
        geo.geocode({'address': self.addressSearch()}, function (results, status) {
            if (status === 'OK') {
                map.setCenter(results[0].geometry.location);
                map.setZoom(14);
                self.getNearbyBreweries(results[0].geometry.location);
                self.addressSearch('');
            } else {
                self.errors.push('Cannot find location');
            }
        });
    };

    this.currentLocationClick = function () {
        // Unused, but leaving for now. Might want it later.

        var pos = {};

        // Get current location
        navigator.geolocation.getCurrentPosition(function (position) {
            pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            map.setCenter(pos);
            map.setZoom(14);
            self.getNearbyBreweries(pos);

            // Get address from current latlng and set search box
            // geo.geocode({'location': pos}, function(results, status) {
            //     if (status === 'OK') {
            //         if (results[0]) {
            //             // Set search box value to most specific address
            //             // returned by reverse geocode. To set to less specific,
            //             // use an index on results higher than 0.
            //             // Example: results[1] = approx location, and results[2] =
            //             // city, state.
            //             input.value = results[0].formatted_address;
            //         }
            //     }
            // });
        });

        // Get breweries surrounding current location

    };

};

initMap();
ko.applyBindings(new ViewModel());
