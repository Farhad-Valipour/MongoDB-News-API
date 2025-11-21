## Description

<!-- Provide a brief description of your changes -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Test updates
- [ ] CI/CD changes
- [ ] Other (please describe):

## Related Issues

<!-- Link to related issues using #issue_number -->

Closes #
Relates to #

## Changes Made

<!-- List the main changes in this PR -->

- 
- 
- 

## Testing

### Test Coverage

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Test coverage maintained/improved (80%+)

### Manual Testing

Describe the manual testing you've done:

```bash
# Commands used for testing
pytest tests/test_feature.py
curl -X GET "http://localhost:8000/api/v1/endpoint"
```

## Documentation

- [ ] Code comments added/updated
- [ ] API Reference updated
- [ ] Usage Examples updated
- [ ] Development Guide updated
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] Docstrings added/updated

## Code Quality

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] No new warnings generated
- [ ] Code is formatted with Black
- [ ] Imports sorted with isort
- [ ] Linted with Flake8
- [ ] Type checked with MyPy

### Pre-commit Checks

```bash
# Run these commands before submitting
black app/ tests/
isort app/ tests/
flake8 app/ tests/
mypy app/
pytest --cov=app --cov-fail-under=80
```

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->

- [ ] This PR introduces breaking changes
- [ ] Migration guide added to documentation

**Breaking Changes:**
<!-- List breaking changes -->

**Migration Path:**
<!-- Describe how users should migrate -->

## Screenshots/Examples

<!-- If applicable, add screenshots or API response examples -->

### Before:
```json
{
  "old_format": "example"
}
```

### After:
```json
{
  "new_format": "example"
}
```

## Deployment Notes

<!-- Any special deployment considerations -->

- [ ] Requires database migration
- [ ] Requires environment variable changes
- [ ] Requires dependency updates
- [ ] Requires server restart

**Environment Variables:**
```env
# New environment variables required
NEW_VAR=value
```

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance degraded (with justification)

**Benchmarks (if applicable):**
```
Before: X requests/sec
After: Y requests/sec
```

## Security Considerations

- [ ] No security impact
- [ ] Security improved
- [ ] Potential security implications (explained below)

**Security Notes:**
<!-- Describe any security considerations -->

## Additional Context

<!-- Add any other context about the PR here -->

## Checklist

<!-- Mark all that apply with an "x" -->

### Before Review
- [ ] I have performed a self-review of my code
- [ ] I have commented complex code sections
- [ ] I have made corresponding changes to documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes have been merged

### Ready for Review
- [ ] This PR is ready for review
- [ ] I have requested specific reviewers (if needed)
- [ ] I have linked related issues

### Post-Review
- [ ] I have addressed all review comments
- [ ] I have re-requested review after changes
- [ ] All conversations are resolved

---

## Reviewer Notes

<!-- Space for reviewers to add notes -->

**Review Checklist for Reviewers:**
- [ ] Code is clear and maintainable
- [ ] Tests are comprehensive
- [ ] Documentation is adequate
- [ ] No security vulnerabilities introduced
- [ ] Performance is acceptable
- [ ] Breaking changes are justified and documented
