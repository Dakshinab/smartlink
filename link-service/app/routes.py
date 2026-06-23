from flask import Blueprint, request, jsonify, redirect
from app import db
from app.models import Link
from app.utils import generate_short_code, is_valid_url, sanitize_custom_slug

# A Blueprint is a way to group related routes together.
# Think of it like a chapter in a book.
links_bp = Blueprint("links", __name__)


@links_bp.route("/health", methods=["GET"])
def health_check():
    """
    Simple health check endpoint.
    DevOps tools (like Kubernetes, load balancers) ping this
    to check if our service is alive.
    Returns 200 OK if everything is fine.
    """
    return jsonify({"status": "healthy", "service": "link-service"}), 200


@links_bp.route("/links", methods=["POST"])
def create_link():
    """
    CREATE a new short link.
    
    Expects JSON body:
    {
        "original_url": "https://example.com/very/long/url",
        "title": "My link",           (optional)
        "custom_slug": "my-link"      (optional)
    }
    
    Returns:
    {
        "short_code": "abc123",
        "short_url": "http://localhost:5001/abc123",
        ...
    }
    """
    data = request.get_json()

    # --- Validation ---
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    original_url = data.get("original_url", "").strip()

    if not original_url:
        return jsonify({"error": "original_url is required"}), 400

    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL. Must start with http:// or https://"}), 400

    # --- Generate or validate short code ---
    custom_slug = data.get("custom_slug", "")

    if custom_slug:
        short_code = sanitize_custom_slug(custom_slug)
        # Check if this slug is already taken
        if Link.query.filter_by(short_code=short_code).first():
            return jsonify({"error": f"Slug '{short_code}' is already taken"}), 409
    else:
        # Auto-generate a unique short code
        # Try up to 5 times in case of collision (very unlikely)
        for _ in range(5):
            short_code = generate_short_code()
            if not Link.query.filter_by(short_code=short_code).first():
                break
        else:
            return jsonify({"error": "Could not generate unique code, try again"}), 500

    # --- Save to database ---
    link = Link(
        short_code=short_code,
        original_url=original_url,
        title=data.get("title", ""),
    )
    db.session.add(link)
    db.session.commit()

    return jsonify(link.to_dict()), 201  # 201 = Created


@links_bp.route("/<short_code>", methods=["GET"])
def redirect_link(short_code):
    """
    REDIRECT user to the original URL.
    This is the main feature - what happens when someone
    visits our short link e.g. slink.io/abc123
    
    Also increments the click counter.
    """
    link = Link.query.filter_by(short_code=short_code, is_active=True).first()

    if not link:
        return jsonify({"error": "Link not found or has been deactivated"}), 404

    # Increment click count
    link.click_count += 1
    db.session.commit()

    # 302 = temporary redirect (browser goes to original_url)
    return redirect(link.original_url, code=302)


@links_bp.route("/links", methods=["GET"])
def list_links():
    """
    LIST all active links.
    Supports pagination via query params:
    /links?page=1&per_page=10
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)

    pagination = Link.query.filter_by(is_active=True)\
        .order_by(Link.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "links": [link.to_dict() for link in pagination.items],
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    }), 200


@links_bp.route("/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    """
    DELETE (deactivate) a link.
    We don't actually delete from the database - 
    we set is_active=False. This is called 'soft delete'.
    It's safer because we keep the history.
    """
    link = Link.query.get(link_id)

    if not link:
        return jsonify({"error": "Link not found"}), 404

    link.is_active = False
    db.session.commit()

    return jsonify({"message": f"Link {link_id} deactivated successfully"}), 200