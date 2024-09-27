from .classes.parser import *

class RouteParser(Parser):
    parser_type = 'route'
    match_keys = ['route', 'route_text_start', 'route_text_end', 'route_text', 'route_readable']
    def normalize_pattern(self):
        route_patterns = []
        for n, p in ROUTES.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the route_patterns array
            route_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(?P<route>' + r'|'.join(route_patterns) + r')', flags = re.I)
        return pattern
    def normalize_match(self, match):
        route = get_normalized(ROUTES, match.group('route'))
        route_text_start, route_text_end = match.span()
        route_text = match[0]
        route_readable = self.get_readable(route=route)
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})
    def get_readable(self, route=None):
        readable = route if route else ''
        return readable

class InhalationRouteParser(RouteParser):
    def normalize_pattern(self):
        route_patterns = []
        for n, p in INHALATION_ROUTES.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the route_patterns array
            route_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(?P<route>' + r'|'.join(route_patterns) + r')', flags = re.I)
        return pattern
    def normalize_match(self, match):
        route = get_normalized(INHALATION_ROUTES, match.group('route'))
        route_text_start, route_text_end = match.span()
        route_text = match[0]
        route_readable = self.get_readable(route=route)
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})

# NOTE: adding \b border because pharmacy was evaluting to topical route of arm
class TopicalRouteParser(RouteParser):
    def normalize_pattern(self):
        topical_route_patterns = []
        for n, p in TOPICAL_ROUTES.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the route_patterns array
            topical_route_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(?P<route>' + r'|'.join(topical_route_patterns) + r')(?!\s?pain)', flags = re.I)
        return pattern
    def normalize_match(self, match):
        route = get_normalized(TOPICAL_ROUTES, match.group('route'))
        route_text_start, route_text_end = match.span()
        route_text = match[0]
        route_readable = self.get_readable(route=route)
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})
    def get_readable(self, route=None):
        readable = route if route else ''
        return readable
    def normalize_multiple_matches(self, matches=[], sig=None):
        # get the min/max start/end locations from list of matches
        route_text_start = min(matches, key=lambda x:x['route_text_start'])['route_text_start']
        route_text_end = max(matches, key=lambda x:x['route_text_end'])['route_text_end']
        # get substring of sig text based on these min/max locations
        route_text = sig[route_text_start:route_text_end]
        # get list of route text from list of matches
        route_list = [m['route'] for m in matches]
        # remove 'topically' from main route list and add to separate list
        # do same for affected area / affected areas
        topical_route = 'topically' in route_list
        affected_areas_route = 'affected areas' in route_list
        affected_area_route = 'affected area' in route_list
        # add topically if we explicitly have 'topically' as a normalized route match
        route_readable = ''
        route_readable += 'topically ' if topical_route else ''
        # prefer 'affected areas' if we have both
        if affected_areas_route:
            route_readable += 'to affected areas '
        elif affected_area_route:
            route_readable += 'to affected area '
        # filter out the above to create a new list of just the sites (i.e. back / torso / hand / etc)
        route_list = [r for r in route_list if r not in ('topically', 'affected areas', 'affected area')]
        if route_list:
            # join with /
            route_list = ' / '.join(route_list)
            # affected areas OF x / y if we have an 'affected areas' match
            # otherwise we would apply TO x / y
            route_readable += ' of ' if (affected_areas_route or affected_area_route) else ' to '
            route_readable += route_list
        # remove white space
        route_readable = route_readable.strip()
        # for now, set route to 'topically' for systems that can't handle specific sites
        route = 'topically'
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})
    def parse(self, sig):
        matches = []
        for match in re.finditer(self.pattern, sig):
            normalized_match = self.normalize_match(match)
            if normalized_match:
                matches.append(normalized_match)
        # once we have matched on all the possible patterns,
        # we take the list of matches and pass it to a special normalize_multiple_matches method
        # which then overwrites the list of matches with one final match that combines all the matches
        if matches:
            normalized_match = self.normalize_multiple_matches(matches, sig)
            if normalized_match:
                matches = [(normalized_match)]
        self.matches = matches
        return matches


class InferredOralRouteParser(RouteParser):
    pattern = r'(?P<route>(?!vaginal|sublingual)tab(?:let)?(?:s)?(?!.*(?:sublingual(?:ly)?|into|per|on the|between the|under|by sublingual route|by buccal route))|cap(?:sule)?(?:s)?|chew(?:able)?|\dpo|capful|pill)'
    def normalize_pattern(self):
        return re.compile(self.pattern, flags = re.I)
    def normalize_match(self, match):
        route = 'by mouth'
        route_text_start, route_text_end = match.span()
        route_text = match[0]
        route_readable = self.get_readable(route=route)
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})


# infers inhalation route for things like 'puffs' in the absence of other more specific routes
class InferredInhalationRouteParser(RouteParser):
    pattern = r'puff(?:s)?(?! in each nostril)(?! in the nose)(?! each nostril)(?! in nostril)'
    def normalize_pattern(self):
        return re.compile(self.pattern, flags = re.I)
    def normalize_match(self, match):
        route = 'into the lungs'
        route_text_start, route_text_end = match.span()
        route_text = match[0]
        route_readable = self.get_readable(route=route)
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})


class MiscellaneousRouteParser(RouteParser):
    def normalize_pattern(self):
        dose_patterns = []
        for n, p in MISCELLANEOUS_ROUTES.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            dose_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(' + r'|'.join(dose_patterns) + r')', flags = re.I)
        return pattern
    def normalize_match(self, match):
        route = 'miscellaneous'
        route_text_start, route_text_end = match.span()
        route_text = match[0]
        route_readable = self.get_readable(route=route)
        return self.generate_match({'route': route, 'route_text_start': route_text_start, 'route_text_end': route_text_end, 'route_text': route_text, 'route_readable': route_readable})


# NOTE: moved InhalationRouteParser above RouteParser here so that "2 PUFFS BY MOUTH DAILY" resolved to "into the lungs" instead of "by mouth"...
#       however, left it in different order above for class inheritance
parsers = [
    InhalationRouteParser(),
    RouteParser(),
    TopicalRouteParser(),
    InferredOralRouteParser(), # turned off for VUMC - TODO: need to create customer "settings"
    InferredInhalationRouteParser(), # turned off for VUMC - TODO: need to create customer "settings"
    MiscellaneousRouteParser(),
]

#print(RouteParser().parse('take one by mouth daily'))